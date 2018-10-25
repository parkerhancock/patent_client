import math
import os
import re
from collections import namedtuple

from lxml import etree as ET
from patent_client.util import Manager
from patent_client.util import Model
from patent_client.util import one_to_one
from PyPDF2 import PdfFileMerger

from .ops import InpadocConnector

whitespace_re = re.compile(" +")
country_re = re.compile(r"^[A-Z]{2}")
ep_case_re = re.compile(r"EP(?P<number>[\d]+)(?P<kind>[A-Z]\d)?")


EpoDoc = namedtuple("EpoDoc", ["number", "kind", "date"])


class InpadocManager(Manager):
    obj_class = "patent_client.epo_ops.models.Inpadoc"
    primary_key = "publication"
    connector = InpadocConnector()

    def __init__(self, *args, **kwargs):
        super(InpadocManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    def __len__(self):
        """Total number of results"""
        if not hasattr(self, "length"):
            self._get_page(1)

        return int(self.length)

    def get_item(self, key):
        if "publication" in self.kwargs:
            doc_db = self.connector.convert_to_docdb(
                self.kwargs["publication"], "publication"
            )
            docs = self.get_by_doc_db(doc_db)
            if type(docs) == list:
                return docs[key]
            return docs
        elif "application" in self.kwargs:
            doc_db = self.connector.convert_to_docdb(
                self.kwargs["application"], "application"
            )
            docs = self.get_by_doc_db(doc_db)
            if type(docs) == list:
                return docs[key]
            return docs
        else:
            # Search Iterator
            page_num = math.floor(key / self.page_size) + 1
            line_num = key % self.page_size
            page = self.connector.get_search_page(self.filter, page_num)
            return self.get_by_doc_db(page[line_num])


class InpadocFullTextManager(InpadocManager):
    def get(self, doc_db):
        data = {
            "description": self.parser.description(doc_db),
            "claims": self.parser.claims(doc_db),
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
            data = self.objects.parser.legal(self.doc_db)
            self._legal = data
        return self._legal

    @property
    def images(self):
        if not hasattr(self, "_images"):
            data = self.objects.parser.images(self.doc_db)
            data["doc_db"] = self.doc_db
            self._images = InpadocImages(data)
        return self._images

    @property
    def family(self):
        return self.objects.get_family(self.doc_db)


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
                self.objects.pdf_request(fname, self.url, params={"Range": i})

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

    def get(self, number=None, doc_type="publication", doc_db=False):
        epodoc = self.convert_to_epodoc(number, doc_type)
        return Epo(epodoc)

    def xml_data(self, pub, data_kind):
        """
        Acceptable kinds are "biblio", "events", "procedural-steps"
        """
        register_url = "http://ops.epo.org/3.2/rest-services/register/{doc_type}/epodoc/{case_number}/"
        if data_kind not in ("biblio", "events", "procedural-steps"):
            raise ValueError(data_kind + " is not a valid data kind")
        url = (
            register_url.format(case_number=pub.case_number, doc_type=pub.doc_type)
            + data_kind
        )
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        return tree


"""
class EpoParser(OPSParser):

    def status(self, el):
        return {
                'description': el.text,
                'code': el.attrib['status-code'],
                'date': el.attrib['change-date'],
            }

    def priority_claim(self, el):
        return {
            'kind': el.attrib['kind'],
            'number': el.find('./reg:doc-number', NS).text,
            'date': el.find('./reg:date', NS).text,
        }


    def docid(self, el):
        doc_id = el.find('.//reg:document-id', NS)
        raw = {
            'country': doc_id.find('./reg:country', NS),
            'number': doc_id.find('./reg:doc-number', NS),
            'kind': doc_id.find('./reg:kind', NS),
            'date': doc_id.find('./reg:date', NS),
        }
        return {k:v.text for (k,v) in raw.items() if v is not None}

    def party(self, el):
        addr_book = el.find('./reg:addressbook', NS)
        name = addr_book.find('./reg:name', NS)
        address = addr_book.find('./reg:address', NS)
        return {
            'name': name.text,
            'address': '\n'.join([t.strip() for t in address.itertext() if t.strip()]).strip()
        }
    
    def citation(self, el):
        phase = el.attrib["cited-phase"]
        office = el.attrib.get("office", "")
        pat_cite = el.find("./reg:patcit", NS)
        if pat_cite is not None:
            citation = self.docid(
                pat_cite
            )
        else:
            citation = el.find("./reg:nplcit/reg:text", NS).text
        category = (
            el.find("./reg:category", NS).text
            if el.find("./reg:category", NS) is not None
            else ""
        )
        relevant_passages = pat_cite.find('./reg:text', NS).text
        return {
            "phase": phase,
            "office": office,
            "citation": citation,
            "category": category,
            "relevant_passages": relevant_passages
        }
    
    def step(self, el):
        date = el.find('./reg:procedural-step-date/reg:date', NS)
        return {
            'phase': el.attrib['procedure-step-phase'],
            'description': ' - '.join([e.text for e in el.findall('./reg:procedural-step-text', NS)]),
            'date': date.text.strip() if date is not None else None,
            'code': el.find('./reg:procedural-step-code', NS).text.strip(),
        }

class Epo():
    objects = EpoManager()

    def __init__(self, epodoc):
        self.epodoc = epodoc
        self.number = epodoc.number
        self.kind = epodoc.kind
        if self.kind == 'A':
            self.doc_type = 'application'
        else:
            self.doc_type = 'publication'
        
        self.dict = self.bib_data
        for k, v in self.dict.items():
            setattr(self, k, v)
    
    def __repr__(self):
        return f'<Epo(number={self.number}, kind={self.kind}, doc_type={self.doc_type})>'

    def __iter__(self):
        return self.dict.items()
    
    @property
    def case_number(self):
        number = f'{self.number}{"." + self.kind if self.kind else ""}'
        return number
    
    @property
    def procedural_steps(self):
        tree = self.objects.xml_data(self, 'procedural-steps')
        doc = tree.find('.//reg:register-document', NS)
        return [self.parse.step(el) for el in doc.find('./reg:procedural-data', NS)]

    @property
    def bib_data(self):
        tree = self.objects.xml_data(self, 'biblio')
        doc = tree.find('.//reg:register-document', NS)
        bib = doc.find('./reg:bibliographic-data', NS)
        parties = bib.find('./reg:parties', NS)
        output = dict()
        output['status'] = [self.parse.status(el) for el in doc.find('./reg:ep-patent-statuses', NS)]
        output['publications'] = [self.parse.docid(el) for el in bib.findall('./reg:publication-reference', NS)]
        output['intl_class'] = [''.join(el.itertext()).strip() for el in bib.find('./reg:classifications-ipcr', NS)]
        output['applications'] = [self.parse.docid(el) for el in bib.findall('./reg:application-reference', NS)]
        output['filing_language'] = bib.find('./reg:language-of-filing', NS).text
        output['priority_claims'] = [self.parse.priority_claim(el) for el in bib.find('reg:priority-claims', NS)]
        output['applicants'] = [self.parse.party(el) for el in parties.find('./reg:applicants', NS)]
        output['inventors'] = [self.parse.party(el) for el in parties.find('./reg:inventors', NS)]
        output['designated_states'] = [c.strip() for c in bib.find('./reg:designation-of-states', NS).itertext() if c.strip()]
        output['title'] = bib.find('./reg:invention-title[@lang="en"]', NS).text
        output['citations'] = [self.parse.citation(el) for el in bib.find('./reg:references-cited', NS)]
        return output
"""
