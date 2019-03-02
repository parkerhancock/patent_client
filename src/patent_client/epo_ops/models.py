import os

from patent_client.epo_ops import CACHE_DIR, TEST_DIR
from patent_client.util import Manager
from patent_client.util import Model
from patent_client.util import one_to_one
from PyPDF2 import PdfFileMerger

from .ops import EpoConnector
from .ops import InpadocConnector

inpadoc_connector = InpadocConnector()
epo_connector = EpoConnector()

SEARCH_FIELDS = {
    "title": "title",
    "abstract": "abstract",
    "title_and_abstract": "titleandabstract",
    "inventor": "inventor",
    "applicant": "applicant",
    "inventor_or_applicant": "inventorandapplicant",
    "publication": "publicationnumber",
    "epodoc_publication": "spn",
    "application": "applicationnumber",
    "epodoc_application": "sap",
    "priority": "prioritynumber",
    "epodoc_priority": "spr",
    "number": "num",  # Pub, App, or Priority Number
    "publication_date": "publicationdate",  # yyyy, yyyyMM, yyyyMMdd, yyyy-MM, yyyy-MM-dd
    "citation": "citation",
    "cited_in_examination": "ex",
    "cited_in_opposition": "op",
    "cited_by_applicant": "rf",
    "other_citation": "oc",
    "family": "famn",
    "cpc_class": "cpc",
    "ipc_class": "ipc",
    "ipc_core_invention_class": "ci",
    "ipc_core_additional_class": "cn",
    "ipc_advanced_class": "ai",
    "ipc_advanced_additional_class": "an",
    "ipc_core_class": "c",
    "classification": "cl",  # IPC or CPC Class
    "full_text": "txt",  # title, abstract, inventor and applicant
}

class InpadocManager(Manager):
    obj_class = "patent_client.epo_ops.models.Inpadoc"
    primary_key = "publication"
    connector = inpadoc_connector
    
    @property
    def allowed_filters(self):
        return list(SEARCH_FIELDS.keys()) + list(SEARCH_FIELDS.values()) + ['cql_query']

    def __init__(self, *args, **kwargs):
        super(InpadocManager, self).__init__(*args, **kwargs)
        self.pages = dict()
        self.connector.test_mode = self.test_mode

    def __len__(self):
        """Total number of results"""
        if "application" in self.config['filter'] or "publication" in self.config['filter']:
            return len(self.get_by_number())
        else:
            try:
                return self.connector.get_search_length(self.config['filter'])
            except Exception:
                return 0

    def get_by_number(self):
        if "publication" in self.config['filter']:
            number = self.config['filter']["publication"]
            if not isinstance(number, list):
                number = number[0]
            doc_db = self.connector.original_to_docdb(number, "publication")
        elif "application" in self.config['filter']:
            number = self.config['filter']["application"]
            if isinstance(number, list):
                number = number[0]
            doc_db = self.connector.original_to_docdb(number, "application")
        docs = self.connector.bib_data(doc_db)
        return docs

    def get_item(self, key):
        if "publication" in self.config['filter'] or "application" in self.config['filter']:
            docs = self.get_by_number()
            return Inpadoc(docs[key])
        else:
            # Search Iterator
            doc_db = self.connector.get_search_item(key, self.config['filter'])
            #return Inpadoc(self.connector.bib_data(doc_db)[0])
            return InpadocResult({**doc_db._asdict(), 'doc_db': doc_db})

    @property
    def query_fields(self):
        for k, v in SEARCH_FIELDS.items():
            print(f"{k} (short form: {v})")

class InpadocResult(Model):
    connector = inpadoc_connector
    
    def __repr__(self):
        return f'<InpadocResult({self.country}{self.number}{self.kind})>'

    @property
    def document(self):
        return Inpadoc(self.connector.bib_data(self.doc_db)[0])

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

    @property
    def specification(self):
        return self.full_text.description

    @property
    def claims(self):
        return self.full_text.claims


class InpadocFullText(Model):
    objects = InpadocFullTextManager()


class InpadocImages(Model):
    objects = InpadocManager()

    def download(self, path="."):
        """Download each page of images, and then consolidate into a single PDF
        Args:
            path: str(base path for file)
        """
        if self.test_mode:
            dirname = (
                TEST_DIR
                / f'{self.doc_db.doc_type}-{self.doc_db.country}{self.doc_db.number}{self.doc_db.kind if self.doc_db.kind else ""}'
            )
        else:

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
