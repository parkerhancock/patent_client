import os
import re
from collections import namedtuple

from lxml import etree as ET
from patent_client.epo_ops import CACHE_DIR
from patent_client.util import Manager
from patent_client.util import Model
from patent_client.util import one_to_one
from PyPDF2 import PdfFileMerger

from .ops import InpadocConnector, EpoConnector

inpadoc_connector = InpadocConnector()
epo_connector = EpoConnector()


class InpadocManager(Manager):
    obj_class = "patent_client.epo_ops.models.Inpadoc"
    primary_key = "publication"
    connector = inpadoc_connector

    def __init__(self, *args, **kwargs):
        super(InpadocManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    def __len__(self):
        """Total number of results"""
        if "application" in self.filter_params or "publication" in self.filter_params:
            return len(self.get_by_number())
        else:
            return self.connector.get_search_length(self.filter_params)

    def get_by_number(self):
        if "publication" in self.kwargs:
            number = self.kwargs["publication"]
            if not isinstance(number, list):
                number = number[0]
            doc_db = self.connector.original_to_docdb(number, "publication")
        elif "application" in self.kwargs:
            number = self.kwargs["application"]
            if isinstance(number, list):
                number = number[0]
            doc_db = self.connector.original_to_docdb(number, "application")
        docs = self.connector.bib_data(doc_db)
        return docs

    def get_item(self, key):
        if "publication" in self.kwargs or "application" in self.kwargs:
            docs = self.get_by_number()
            return Inpadoc(docs[key])
        else:
            # Search Iterator
            doc_db = self.connector.get_search_item(key, self.filter_params)
            return Inpadoc(self.connector.bib_data(doc_db)[0])


class InpadocFullTextManager(InpadocManager):
    def get(self, doc_db):
        data = {
            "description": self.connector.description(doc_db),
            "claims": self.connector.claims(doc_db),
            "doc_db": doc_db,
        }
        return InpadocFullText(data)


class Inpadoc(Model):
    objects = InpadocManager()
    full_text = one_to_one(
        "patent_client.epo_ops.models.InpadocFullText", doc_db="doc_db"
    )
    us_application = one_to_one(
        "patent_client.USApplication", appl_id="original_application_number"
    )

    def __repr__(self):
        return f"<Inpadoc(publication={self.publication})>"

    @property
    def legal(self):
        if not hasattr(self, "_legal"):
            data = inpadoc_connector.legal(self.doc_db)
            self._legal = data
        return self._legal

    @property
    def images(self):
        if not hasattr(self, "_images"):
            data = inpadoc_connector.images(self.doc_db)
            data["doc_db"] = self.doc_db
            self._images = InpadocImages(data)
        return self._images

    @property
    def family(self):
        for doc_db in inpadoc_connector.family(self.doc_db):
            yield Inpadoc(inpadoc_connector.bib_data(doc_db)[0])


class InpadocFullText(Model):
    objects = InpadocFullTextManager()


class InpadocImages(Model):
    objects = InpadocManager()

    def download(self, path="."):
        """Download each page of images, and then consolidate into a single PDF
        Args:
            path: str(base path for file)
        """
        dirname = (
            CACHE_DIR
            / f'{self.doc_db.doc_type}-{self.doc_db.country}{self.doc_db.number}{self.doc_db.kind if self.doc_db.kind else ""}'
        )
        dirname.mkdir(exist_ok=True)
        for i in range(1, self.num_pages + 1):
            fname = dirname / ("page-" + str(i).rjust(6, "0") + ".pdf")
            if not fname.exists():
                inpadoc_connector.pdf_request(fname, self.url, params={"Range": i})

        pages = list(sorted(os.listdir(dirname)))
        out_file = PdfFileMerger()
        for p in pages:
            out_file.append(os.path.join(dirname, p))
        out_fname = os.path.join(
            path, self.doc_db.country + self.doc_db.number + ".pdf"
        )
        out_file.write(out_fname)


class EpoManager(Manager):
    """
    EPO Manager
    This is a manager class to the EPO register. Retrieves information about
    EPO patents and applications
    """

    obj_class = "patent_client.epo_ops.models.Epo"

    def get(self, number=None, doc_type="publication"):
        epodoc = epo_connector.original_to_epodoc(number, doc_type)
        bib_data = epo_connector.bib_data(epodoc)
        return Epo(bib_data)


class Epo(Model):
    objects = EpoManager()

    def __repr__(self):
        return (
            f"<Epo(number={self.number}, kind={self.kind}, doc_type={self.doc_type})>"
        )

    @property
    def procedural_steps(self):
        return epo_connector.procedural_steps(self.epodoc)

