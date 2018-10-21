import lxml.etree as ET
import re
import os
import math
import requests
from tempfile import TemporaryDirectory
from PyPDF2 import PdfFileMerger
import json
from hashlib import md5
from ip import SETTINGS, CACHE_BASE
from collections import namedtuple

from ip.util import BaseSet, one_to_many, one_to_one

# XML Namespaces for ElementTree
NS = {
    "ops": "http://ops.epo.org",
    "epo": "http://www.epo.org/exchange",
    "ft": "http://www.epo.org/fulltext",
    "reg": "http://www.epo.org/register",
}

CLIENT_SETTINGS = SETTINGS['EpoOpenPatentServices']
KEY = CLIENT_SETTINGS['ApiKey']
SECRET = CLIENT_SETTINGS['Secret']
CACHE_DIR = CACHE_BASE / 'epo'
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()
whitespace_re = re.compile(" +")
country_re = re.compile(r"^[A-Z]{2}")
ep_case_re = re.compile(r'EP(?P<number>[\d]+)(?P<kind>[A-Z]\d)?')


DocDB = namedtuple('DocDB', ['country', 'number', 'kind', 'date'])
EpoDoc = namedtuple('EpoDoc', ['number', 'kind', 'date'])

class OPSException(Exception):
    pass

class OPSAuthenticationException(OPSException):
    pass


class OPSParser:
    """Internal xml parsing class for common tasks"""
    def docdb_number(self, el):
        raw_data = {
            "country": el.find("./epo:country", NS),
            "number": el.find("./epo:doc-number", NS),
            "kind": el.find("./epo:kind", NS),
            "date": el.find("./epo:date", NS),
        }
        for k, v in raw_data.items():
            if v is not None:
                raw_data[k] = v.text

        return DocDB(**raw_data)
    
    def epodoc_number(self, el):
        raw_data = {
            "number": el.find("./epo:doc-number", NS),
            "kind": el.find("./epo:kind", NS),
            "date": el.find("./epo:date", NS),
        }
        for k, v in raw_data.items():
            if v is not None:
                raw_data[k] = v.text

        return EpoDoc(**raw_data)

    def cpc_class(self, el):
        keys = "section, class, subclass, main-group, subgroup".split(", ")
        data = {k: el.find("./epo:" + k, NS) for k in keys}
        data = {k: v.text for (k, v) in data.items() if v is not None}
        return f"{data.get('section', '')}{data.get('class', '')}{data.get('subclass', '')} {data.get('main-group', '')}/{data.get('subgroup', '')}"


    def pct_to_docdb(self, number):
        _, country_year, number = number.split("/")
        country, year = country_year[:2], country_year[2:]
        if len(year) == 2:
            if int(year) > 50:
                year = "19" + year
            else:
                year = "20" + year

        # DocDB format changed in 2004:
        # Pre-2003 - CCyynnnnnW
        # Post-2003 - CCccyynnnnnnW
        if int(year) >= 2004:
            case_number = year + number.rjust(6, "0")
        else:
            case_number = year[2:] + number.rjust(5, "0")
        return DocDB(country, case_number, 'W', None)


    def citation(self, el):
        phase = el.attrib["cited-phase"]
        cited_by = el.attrib["cited-by"]
        office = el.attrib.get("office", "")
        pat_cite = el.find("./epo:patcit", NS)
        if pat_cite is not None:
            citation = dict(self.docdb_number(
                pat_cite.find('./epo:document-id[@document-id-type="docdb"]', NS)
            )._asdict())
        else:
            citation = el.find("./epo:nplcit/epo:text", NS).text
        category = (
            el.find("./epo:category", NS).text
            if el.find("./epo:category", NS) is not None
            else ""
        )
        relevant_claims = el.find("./epo:rel-claims", NS)
        relevant_passages = [
            e.text for e in el.findall("./epo:rel-passage/epo:passage", NS)
        ]
        return {
            "phase": phase,
            "cited_by": cited_by,
            "office": office,
            "citation": citation,
            "category": category,
            "relevant_claims": relevant_claims.text if relevant_claims is not None else "",
            "relevant_passages": relevant_passages,
        }


class OPSManager:
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
        print(url)
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
                raise OPSException(f"{response.status_code} - {code} - {message}")
            retry += 1
        raise OPSException("Max Retries Exceeded!")



    def xml_request(self, url, params=dict()):
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
            return self.parser.docdb_number(app_ref)
        elif doc_type == "publication":
            pub_ref = output.find("./ops:publication-reference/epo:document-id", NS)
            return self.parser.docdb_number(pub_ref)
    
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
    """
    INPADOC

    This is a manager class. Provides access to:
    .get => Retrieve an Inpadoc record
    .search => Search based on various criteria. Similar to Espacenet Smart Search.
    """
    def get(self, number=None, doc_type="publication", doc_db=False):
        if not doc_db:
            if 'PCT' in number:
                doc_type = 'application'
                doc_db = self.parser.pct_to_docdb(number)
            else:
                doc_db = self.convert_to_docdb(number, doc_type)
        return Inpadoc(doc_type, doc_db)
    
    def search(self, query):
        return InpadocSet(InpadocSearch(query))
    
    def filter(self, query):
        return self.search(query)

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
        print(url)
        tree = ET.fromstring(text.encode("utf-8"))
        return tree

class Inpadoc():
    """
    INPADOC Publication

    This is a lazy-loading object that accesses INPADOC data for the associated class.
    
    The first time any data is accessed, the result is fetched and then cached on the object.

    Data includes:
        bib_data => Basic bibliogrpahic information + Abstract
        description => Full Text Specification
        claims => Claims text
        images => Images listing
        download_images() => download a PDF of the published document
        legal => Status Information

    """

    objects = InpadocManager()
    us_application = one_to_one('ip.USApplication', publication='publication')

    def __init__(self, doc_type="publication", doc_db=False):
        self.doc_type = doc_type
        self.doc_db = doc_db
        self.country = doc_db.country
        self.number = doc_db.number
        self.kind = doc_db.kind
        self.date = doc_db.date
        self.dict = self.bib_data
        for k, v in self.dict.items():
            if not hasattr(self, k):
                setattr(self, k, v)

    def __repr__(self):
        return f'<Inpadoc({self.country}{self.number}, {self.doc_type})>'

    def __iter__(self):
        return iter(self.dict.items())

    @property
    def legal(self):
        tree = self.objects.xml_data(self, 'legal')
        legal_events = tree.findall('.//ops:legal', NS)
        output=list()
        for le in legal_events:
            row = dict()
            row['description'] = le.attrib['desc']
            row['explanation'] = le.attrib['infl']
            row['code'] = le.attrib['code'].strip()
            row['date'] = le.find('./ops:L007EP', NS).text
            output.append(row)
        output = list(sorted(output, key=lambda x: x['date']))
        return output

    @property
    def bib_data(self):
        # NOTE: For EP cases with search reports, there is citation data in bib data
        # We just currently are not parsing it
        tree = self.objects.xml_data(self, "biblio")
        document = tree.find("./epo:exchange-documents/epo:exchange-document", NS)
        data = dict()
        bib_data = document.find("./epo:bibliographic-data", NS)

        title = bib_data.find("./epo:invention-title[@lang='en']", NS)
        if title == None:
            title = bib_data.find("./epo:invention-title", NS)
        if title != None:
            data["title"] = title.text.strip()
        else:
            data["title"] = ""
        pub_data = bib_data.find(
            './epo:publication-reference/epo:document-id[@document-id-type="docdb"]',
            NS,
        )
        pub_data = dict(self.objects.parser.docdb_number(pub_data)._asdict())
        data["publication"] = pub_data['country'] + pub_data['number'] + pub_data['kind']
        data["publication_date"] = pub_data.get('date', None)
        data["country"] = pub_data['country']


        app_data = bib_data.find(
            './epo:application-reference/epo:document-id[@document-id-type="docdb"]',
            NS,
        )
        app_data = dict(self.objects.parser.docdb_number(app_data)._asdict())
        data["application"] = app_data['country'] + app_data['number']
        data["filing_date"] = app_data.get('date', None)

        intl_class = [
            whitespace_re.sub("", e.text)
            for e in bib_data.findall(
                "./epo:classifications-ipcr/epo:classification-ipcr/epo:text", NS
            )
        ]
        data["intl_class"] = intl_class

        cpc_classes = bib_data.findall(
            "./epo:patent-classifications/epo:patent-classification", NS
        )
        data["cpc_class"] = [self.objects.parser.cpc_class(el) for el in cpc_classes]

        priority_apps = bib_data.findall(
            './epo:priority-claims/epo:priority-claim/epo:document-id[@document-id-type="original"]/epo:doc-number',
            NS,
        )
        data["priority_claims"] = [e.text for e in priority_apps]

        parties = bib_data.find("./epo:parties", NS)
        data["applicants"] = [
            e.text
            for e in parties.findall(
                './epo:applicants/epo:applicant[@data-format="original"]/epo:applicant-name/epo:name',
                NS,
            )
        ]
        data["inventors"] = [
            e.text
            for e in parties.findall(
                './epo:inventors/epo:inventor[@data-format="original"]/epo:inventor-name/epo:name',
                NS,
            )
        ]
        abstract = document.find('./epo:abstract[@lang="en"]', NS)
        data["abstract"] = (
            "".join(t for t in abstract.itertext()).strip()
            if abstract is not None
            else ""
        )

        refs_cited = bib_data.findall("./epo:references-cited/epo:citation", NS)
        data["references_cited"] = [self.objects.parser.citation(c) for c in refs_cited]
        
        return data


    @property
    def description(self):
        tree = self.objects.xml_data(self, "description")
        description = tree.find(
            "./ft:fulltext-documents/ft:fulltext-document/ft:description", NS
        )
        text = "\n".join(description.itertext()).strip()
        return text

    @property
    def claims(self):
        tree = self.objects.xml_data(self, "claims")
        claims = [
            "".join(e.itertext()).strip()
            for e in tree.findall(
                './ft:fulltext-documents/ft:fulltext-document/ft:claims[@lang="EN"]/ft:claim/ft:claim-text',
                NS,
            )
        ]
        return claims

    @property
    def images(self):
        tree = self.objects.xml_data(self, "images")
        images = tree.find(
            './ops:document-inquiry/ops:inquiry-result/ops:document-instance[@desc="FullDocument"]',
            NS,
        )
        data = {
            "url": "http://ops.epo.org/rest-services/" + images.attrib["link"] + ".pdf",
            "num_pages": int(images.attrib["number-of-pages"]),
            "sections": {
                e.attrib["name"]: int(e.attrib["start-page"])
                for e in images.findall("./ops:document-section", NS)
            },
        }
        return data
    
    @property
    def family(self):
        tree = self.objects.xml_data(self, 'family')
        doc_db_list = list()
        for el in tree.findall("./ops:patent-family/ops:family-member", NS):
            pub_ref = el.find(
                './epo:publication-reference/epo:document-id[@document-id-type="docdb"]',
                NS,
            )
            if pub_ref is not None:
                doc_db_list.append((self.objects.parser.docdb_number(pub_ref), 'publication'))
            else:
                app_ref = el.find(
                    './epo:application-reference/epo:document-id[@document-id-type="docdb"]',
                    NS
                )
                doc_db_list.append((self.objects.parser.docdb_number(app_ref), 'application'))
        return InpadocSet(doc_db_list) 


    def download_images(self, path="."):
        """Download each page of images, and then consolidate into a single PDF
        Args:
            path: str(base path for file)
        """
        img_data = self.images
        dirname = CACHE_DIR / f'{self.doc_type}-{self.country}{self.number}{self.kind if self.kind else ""}'
        dirname.mkdir(exist_ok=True)
        for i in range(1, img_data["num_pages"] + 1):
            fname = dirname / ("page-" + str(i).rjust(6, "0") + ".pdf")
            if not fname.exists():
                self.objects.pdf_request(fname, img_data['url'], params={"Range": i})

        pages = list(sorted(os.listdir(dirname)))
        out_file = PdfFileMerger()
        for p in pages:
            out_file.append(os.path.join(dirname, p))
        out_fname = os.path.join(
            path, self.country + self.number + ".pdf"
        )
        out_file.write(out_fname)

class InpadocSet(BaseSet):
    def __init__(self, doc_db_list):
        self.objs = doc_db_list

    def __repr__(self):
        return f'<InpadocSet(len={len(self)})>'

    def __len__(self):
        return len(self.objs)

    def __getitem__(self, key):
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            doc_db, doc_type = self.objs[key]            
            return Inpadoc(doc_db=doc_db, doc_type=doc_type)

    def __add__(self, other):
        return InpadocSet(self.objs + other.objs)

    def __iter__(self):
        return (Inpadoc(doc_db=doc_db, doc_type=doc_type) for (doc_db, doc_type) in self.objs)


class InpadocSearch(OPSManager):
    """ 
    INPADOC Search

    This provides an interface to the EPO's INPADOC search functionality.
    This class is effectively a generator for accesssing paginated search results.
    This is accessed through the Inpadoc interface class.
    
    Query is in the CQL format, explained in the OPS documentation appendix
    http://documents.epo.org/projects/babylon/eponet.nsf/0/F3ECDCC915C9BCD8C1258060003AA712/$File/ops_v3.2_documentation_-_version_1.3.6_en.pdf
    """
    search_url = 'http://ops.epo.org/3.2/rest-services/published-data/search'
    parser = OPSParser()
    page_size=25

    def __init__(self, query):
        self.query = dict(q=query)
        text = self.xml_request(self.search_url, self.query)
        tree = ET.fromstring(text.encode("utf-8"))
        self.length = tree.find(".//ops:biblio-search", NS).attrib['total-result-count']
        self.pages = {1: text}
    
    def __len__(self):
        """Total number of results"""
        return int(self.length)

    def __getitem__(self, key):
        """Supports indexing and slicing results"""
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            page_num = math.floor(key / self.page_size) + 1
            line_num = key % self.page_size
            page = self._get_page(page_num)
            return (page[line_num], 'publication')

    def _get_page(self, page_num):
        """Internal private method for handling pages of results"""
        if page_num not in self.pages:
            start = (page_num - 1) * self.page_size + 1
            end = start + self.page_size - 1 
            query = {**self.query, **{'Range': f'{start}-{end}'}}
            self.pages[page_num] = self.xml_request(self.search_url, query)
        text = self.pages[page_num]
        tree = ET.fromstring(text.encode('utf-8'))
        results = tree.find('.//ops:search-result', NS)
        return [self.parser.docdb_number(el.find('./epo:document-id', NS)) for el in results]
      

class EpoManager(OPSManager):
    """
    EPO Manager

    This is a manager class to the EPO register. Retrieves information about
    EPO patents and applications

    """
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