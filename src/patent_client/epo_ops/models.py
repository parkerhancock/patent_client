import re
import os
import math
import requests
from lxml import etree as ET
from tempfile import TemporaryDirectory
from PyPDF2 import PdfFileMerger
import json
from hashlib import md5
from patent_client import SETTINGS, CACHE_BASE
from collections import namedtuple

from patent_client.util import Manager, one_to_many, one_to_one, Model
from .parsers import OPSParser, InpadocParser

# XML Namespaces for ElementTree
NS = {
    "ops": "http://ops.epo.org",
    "epo": "http://www.epo.org/exchange",
    "ft": "http://www.epo.org/fulltext",
    "reg": "http://www.epo.org/register",
}

CLIENT_SETTINGS = SETTINGS['EpoOpenPatentServices']
if os.environ.get('EPO_KEY', False):
    KEY = os.environ['EPO_KEY']
    SECRET = os.environ['EPO_SECRET']
else:
    KEY = CLIENT_SETTINGS['ApiKey']
    SECRET = CLIENT_SETTINGS['Secret']
CACHE_DIR = CACHE_BASE / 'epo'
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()
whitespace_re = re.compile(" +")
country_re = re.compile(r"^[A-Z]{2}")
ep_case_re = re.compile(r'EP(?P<number>[\d]+)(?P<kind>[A-Z]\d)?')


DocDB = namedtuple('DocDB', ['country', 'number', 'kind', 'date', 'doc_type'])
EpoDoc = namedtuple('EpoDoc', ['number', 'kind', 'date'])

SEARCH_FIELDS = {
    'title': 'title',
    'abstract': 'abstract',
    'title_and_abstract': 'titleandabstract',
    'inventor': 'inventor',
    'applicant': 'applicant',
    'inventor_or_applicant': 'inventorandapplicant',
    'publication': 'publicationnumber',
    'epodoc_publication': 'spn',
    'application': 'applicationnumber',
    'epodoc_application': 'sap',
    'priority': 'prioritynumber',
    'epodoc_priority': 'spr',
    'number': 'num', # Pub, App, or Priority Number
    'publication_date': 'publicationdate', # yyyy, yyyyMM, yyyyMMdd, yyyy-MM, yyyy-MM-dd
    'citation': 'citation',
    'cited_in_examination': 'ex',
    'cited_in_opposition': 'op',
    'cited_by_applicant': 'rf',
    'other_citation': 'oc',
    'family': 'famn',
    'cpc_class' : 'cpc',
    'ipc_class': 'ipc',
    'ipc_core_invention_class': 'ci',
    'ipc_core_additional_class': 'cn',
    'ipc_advanced_class': 'ai',
    'ipc_advanced_additional_class': 'an',
    'ipc_advanced_class': 'a',
    'ipc_core_class': 'c',
    'classification': 'cl', #IPC or CPC Class
    'full_text': 'txt', #title, abstract, inventor and applicant
}

class OPSException(Exception):
    pass

class OPSAuthenticationException(OPSException):
    pass

class OPSManager(Manager):
    """
    Base Class for clients based on the EPO Open Patent Services
    Includes INPADOC and EPO Register
    """
    parser = OPSParser()

    def authenticate(self, key=None, secret=None):
        auth_url = "https://ops.epo.org/3.2/auth/accesstoken"
        global KEY, SECRET
        if key:
            KEY=key
            SECRET=secret

        response = session.post(
            auth_url, auth=(KEY, SECRET), data={"grant_type": "client_credentials"}
        )

        if not response.ok:
            raise OPSAuthenticationException()

        access_token = response.json()["access_token"]
        session.headers["Authorization"] = "Bearer " + access_token

    def pdf_request(self, fname, url, params=dict()):
        if os.path.exists(fname):
            return
        else:
            with open(fname, 'wb') as f:
                response = self.request(url, params, stream=True)
                f.write(response.raw.read())

    
    def request(self, url, params=dict(), stream=False):
        retry = 0
        while retry < 3:
            response = session.get(url, params=params, stream=stream)
            if response.ok:
                return response
            elif response.status_code in (400, 403):
                self.authenticate()
            elif not response.ok:
                tree = ET.fromstring(response.text.encode("utf-8"))
                code = tree.find("./ops:code", NS).text
                message = tree.find("./ops:message", NS).text
                details = tree.find('./ops:details', NS)
                if details is not None:
                    details = ''.join(details.itertext())
                else:
                    details = '<None>'
                raise OPSException(f"{response.status_code} - {code} - {message}\nDETAILS: {details} \nURL: {response.request.url}")
            retry += 1
        raise OPSException("Max Retries Exceeded!")



    def xml_request(self, url, params=dict()):
        print(url, params)
        param_hash = md5(json.dumps(params, sort_keys=True).encode('utf-8')).hexdigest()
        fname = os.path.join(CACHE_DIR, f"{url[37:].replace('/', '_')}{param_hash if params else ''}.xml")
        if os.path.exists(fname):
            return open(fname).read()
        response = self.request(url, params)
        text = response.text
        with open(fname, "w") as f:
            f.write(text)
        return text
        
    
    def convert_to_docdb(self, number, doc_type):
        if 'PCT' in number:
            return self.parser.pct_to_docdb(number)

        country = country_re.search(number)
        if country:
            country = country.group(0)
            number = number[2:]
        else:
            country = "US"
            number = number

        url = f"http://ops.epo.org/3.2/rest-services/number-service/{doc_type}/original/{country}.({number})/docdb"
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        output = tree.find("./ops:standardization/ops:output", NS)

        if doc_type == "application":
            app_ref = output.find("./ops:application-reference/epo:document-id", NS)
            return self.parser.docdb_number(app_ref, doc_type)
        elif doc_type == "publication":
            pub_ref = output.find("./ops:publication-reference/epo:document-id", NS)
            return self.parser.docdb_number(pub_ref, doc_type)
    
    def convert_to_epodoc(self, number, doc_type):
        url = f"http://ops.epo.org/3.2/rest-services/number-service/{doc_type}/original/{number})/epodoc"
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        output = tree.find("./ops:standardization/ops:output", NS)

        if doc_type == "application":
            app_ref = output.find("./ops:application-reference/epo:document-id", NS)
            return self.parser.epodoc_number(app_ref)
        elif doc_type == "publication":
            pub_ref = output.find("./ops:publication-reference/epo:document-id", NS)
            return self.parser.epodoc_number(pub_ref)



class InpadocManager(OPSManager):
    page_size = 25
    search_url = 'http://ops.epo.org/3.2/rest-services/published-data/search'
    obj_class = 'patent_client.epo_ops.models.Inpadoc'


    def __init__(self, *args, **kwargs):
        super(InpadocManager, self).__init__(*args, **kwargs)
        self.parser = InpadocParser(self)
        self.pages = dict()
    
    def get(self, *args, **kwargs):
        args = [a for a in args + self.args if a]
        manager = self.filter(*args, **{**self.kwargs, **kwargs})
        if len(manager) > 1:
            doc_nos = '\n'.join([r.publication for r in manager])
            raise OPSException('More than one document found!\n' + doc_nos)
        return manager.first()
        
    def get_by_doc_db(self, doc_db):
        bib_data = self.parser.bib_data(doc_db)
        if len(bib_data) > 1:
            return list(Inpadoc(b) for b in bib_data)
        else:
            return Inpadoc(bib_data[0])

    def __len__(self):
        """Total number of results"""
        if not hasattr(self, 'length'):
            self._get_page(1)

        return int(self.length)

    def get_item(self, key):
        # Application Iterator
        if 'application' in self.kwargs:
            doc_db = self.convert_to_docdb(self.kwargs['application'], 'application')
            docs = self.get_by_doc_db(doc_db)
            if type(docs) == list:
                return docs[key]
            return docs

        # Search Iterator
        page_num = math.floor(key / self.page_size) + 1
        line_num = key % self.page_size
        page = self._get_page(page_num)
        return self.get_by_doc_db(page[line_num])

    def _get_page(self, page_num):
        """Internal private method for handling pages of results"""
        if page_num not in self.pages:
            start = (page_num - 1) * self.page_size + 1
            end = start + self.page_size - 1 
            query = {**self.create_query(), **{'Range': f'{start}-{end}'}}
            self.pages[page_num] = self.xml_request(self.search_url, query)
        text = self.pages[page_num]
        tree = ET.fromstring(text.encode('utf-8'))
        self.length = int(tree.find('.//ops:biblio-search', NS).attrib['total-result-count'])
        results = tree.find('.//ops:search-result', NS)
        return [self.parser.docdb_number(el.find('./epo:document-id', NS), 'publication') for el in results]
    
    def get_family(self, doc_db):
        family = self.parser.family(doc_db)
        return list(self.get_by_doc_db(doc_db=d) for d in family)


    def filter(self, *args, **kwargs):
        if len(args) > 0:
            if 'PCT' in args[0]:
                kwargs['application'] = args[0]
            else:
                kwargs['publication'] = args[0]
        return self.__class__(**{**self.kwargs, **kwargs})

    def create_query(self):
        query = ''
        for keyword, value in self.kwargs.items():
            if "values__" in keyword:
                continue
            if len(value.split()) > 1:
                value = f'"{value}"'
            query += SEARCH_FIELDS[keyword] + '=' + value
        return dict(q=query)
        

    def xml_data(self, pub, data_kind):
        """
        Acceptable kinds are "biblio", "description", "claims", "images", "legal", or "family
        """
        case_number = f'{pub.country}.{pub.number}{"." + pub.kind if pub.kind else ""}'

        if data_kind not in ("biblio", "description", "claims", "images", "legal", "family"):
            raise OPSException(data_kind + " is not a valid data kind")
        if data_kind == 'legal':
            legal_url = "http://ops.epo.org/3.2/rest-services/legal/{doc_type}/docdb/{case_number}/"
            url = legal_url.format(
                case_number=case_number,
                doc_type=pub.doc_type,
            )
        elif data_kind == 'family':
            family_url = "http://ops.epo.org/3.2/rest-services/family/{doc_type}/docdb/{case_number}/"
            url = family_url.format(case_number=case_number, doc_type=pub.doc_type)
        else:
            data_url = "http://ops.epo.org/3.2/rest-services/published-data/{doc_type}/docdb/{case_number}/{data_kind}"
            url = data_url.format(
                case_number=case_number, 
                doc_type=pub.doc_type, 
                data_kind=data_kind,
            )
        text = self.xml_request(url)
        tree = ET.fromstring(text.encode("utf-8"))
        return tree

class InpadocFullTextManager(InpadocManager):
    def get(self, doc_db):
        data = {
            'description': self.parser.description(doc_db),
            'claims': self.parser.claims(doc_db),
            'doc_db': doc_db,
        }
        return InpadocFullText(data)

class Inpadoc(Model):
    objects = InpadocManager()
    full_text = one_to_one('patent_client.epo_ops.models.InpadocFullText', doc_db='doc_db')
    us_application = one_to_one('patent_client.USApplication', appl_id='original_application_number')

    def __repr__(self):
        return f'<Inpadoc(publication={self.publication})>'

    @property
    def legal(self):
        if not hasattr(self, '_legal'):
            data = self.objects.parser.legal(self.doc_db)
            self._legal = data
        return self._legal

    @property
    def images(self):
        if not hasattr(self, '_images'):
            data = self.objects.parser.images(self.doc_db)
            data['doc_db'] = self.doc_db
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
        dirname = CACHE_DIR / f'{self.doc_db.doc_type}-{self.doc_db.country}{self.doc_db.number}{self.doc_db.kind if self.doc_db.kind else ""}'
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


      

class EpoManager(OPSManager):
    """
    EPO Manager
    This is a manager class to the EPO register. Retrieves information about
    EPO patents and applications
    """
    obj_class = 'patent_client.epo_ops.models.Epo'

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
        tree = ET.fromstring(text.encode('utf-8'))
        return tree
        
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
    parse = EpoParser()

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