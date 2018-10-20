import json
import os
import time
from hashlib import sha1

from zipfile import ZipFile
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from datetime import date
from dateutil.parser import parse as parse_dt
import json
import re
from copy import deepcopy
import os
import warnings

import inflection
import requests

from ip import CACHE_BASE
from ip.util import BaseSet, hash_dict, one_to_one, one_to_many, Model

class HttpException(Exception):
    pass


class NotAvailableException(Exception):
    pass



CHUNK_SIZE = 25
QUERY_URL = "https://ped.uspto.gov/api/queries"
BASE_URL = "https://ped.uspto.gov/api/"
PACKAGE_URL = "https://ped.uspto.gov/api/queries/{query_id}/package"
STATUS_URL = "https://ped.uspto.gov/api/queries/{query_id}"
DOWNLOAD_URL = "https://ped.uspto.gov/api/queries/{query_id}/download"
QUERY_FIELDS = 'appEarlyPubNumber applId appLocation appType appStatus_txt appConfrNumber appCustNumber appGrpArtNumber appCls appSubCls appEntityStatus_txt patentNumber patentTitle primaryInventor firstNamedApplicant appExamName appExamPrefrdName appAttrDockNumber appPCTNumber appIntlPubNumber wipoEarlyPubNumber pctAppType firstInventorFile appClsSubCls rankAndInventorsList'

CACHE_DIR = CACHE_BASE / 'uspto_examination_data'
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers["User-Agent"] = "python-ip"


class USApplicationManager(BaseSet):
    primary_key = 'appl_id'

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def filter(self, *args, **kwargs):
        return self.__class__(*args, *self.args, **{**kwargs, **self.kwargs})

    def order_by(self, *args):
        kwargs = deepcopy(self.kwargs)
        if 'sort' not in kwargs:
            kwargs['sort'] = list()
        kwargs['sort'] += args
        return self.__class__(*self.args, **{**kwargs, **self.kwargs})

    def first(self):
        return self[0]

    def all(self):
        return iter(self)
    
    def __getitem__(self, key):
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            if not hasattr(self, 'objs'):
                self.request()
            return self.objs[key]
    
    def __len__(self):
        if not hasattr(self, '_len'):
            self.request()
        return self._len

    def count(self):
        return len(self)

    def get(self, *args, **kwargs):
        if 'publication' in kwargs:
            if 'A1' in kwargs['publication']:
                warnings.warn('Lookup by Publication does not work well')
                kwargs['app_early_pub_number'] = kwargs['publication']
            else:
                kwargs['patent_number'] = kwargs['publication'][2:-2]
            del kwargs['publication']
        manager = self.__class__(*args, *self.args, **{**kwargs, **self.kwargs})
        count = manager.count()
        if count > 1:
            raise ValueError('More than one result!')
        elif count == 0:
            raise ValueError('Object Not Found!')
        else:
            return manager.first()

    def get_many(self, *args, **kwargs):
        manager = self.__class__(*args, *self.args, **{**kwargs, **self.kwargs, **dict(default_connector='OR')})
        return manager



    def _generate_query(self, params=dict()):
        params = {**{self.primary_key: self.args}, **self.kwargs, **params}
        default_connector = params.get('default_connector', 'AND')
        if 'default_connector' in params: del params['default_connector']
        sort_query = ''

        if 'sort' in params:
            for s in params['sort']:
                if s[0] == '-':
                    sort_query += f'{inflection.camelize(s[1:], uppercase_first_letter=False)} desc '
                else:
                    sort_query += f'{inflection.camelize(s, uppercase_first_letter=False)} asc'

            del params['sort']

        query = ''
        for k, v in params.items():
            field = inflection.camelize(k, uppercase_first_letter=False)
            if not v:
                continue            
            elif type(v) in (list, tuple):
                body = f' {default_connector} '.join(v)
            else:
                body = v
            query += f'{field}:({body}) '
            
            #import pdb; pdb.set_trace()
        mm = '100%' if 'appEarlyPubNumber' not in query else '90%'

        return {
            "qf": QUERY_FIELDS,
            "fl": '*',
            "searchText": query.strip(),
            "sort": sort_query.strip(),
            "facet": "false",
            "mm": mm,
        }

        

    def request(self, params=dict()):
        query_params = self._generate_query(params)
        fname = hash_dict(query_params) + '.json'
        fname = os.path.join(CACHE_DIR, fname)
        print(json.dumps(query_params, indent=2))
        if not os.path.exists(fname):
            response = session.post(QUERY_URL, json=query_params)
            if not response.ok:
                if "requested resource is not available" in response.text:
                    raise NotAvailableException("Patent Examination Data is Offline")
                else:
                    raise HttpException(
                        f"{response.status_code}\n{response.text}\n{response.headers}"
                    )
            data = response.json()
        else:
            data = json.load(open(fname))
        results = data["queryResults"]["searchResponse"]["response"]
        num_found = results['numFound']
        self._len = num_found
        if num_found <= 20:
            with open(fname, 'w') as f:
                json.dump(data, f, indent=2)
            self.objs = USApplicationJsonSet(results['docs'], num_found)
        else:
            return self._package_xml(query_params,data)
    
    def _package_xml(self, query_params, data):
        fname = hash_dict(query_params) + ".zip"
        fname = os.path.join(CACHE_DIR, fname)
        query_id = data["queryId"]
        results = data["queryResults"]["searchResponse"]["response"]
        num_found = results['numFound']
        if not os.path.exists(fname):
            time.sleep(0.5)
            response = session.put(
                PACKAGE_URL.format(query_id=query_id), params={"format": "XML"}
            )
            if not response.ok:
                print(response.request.url)
                print(response.status_code)
                print(response.text)
                raise HttpException("Packaging Request Failed!")

            start = time.time()
            while time.time() - start < 60:
                response = session.get(STATUS_URL.format(query_id=query_id))
                if not response.ok:
                    raise HttpException("Status Request Failed!")
                status = response.json()["jobStatus"]
                if status == "COMPLETED":
                    break
                time.sleep(1)
            if status != "COMPLETED":
                raise HttpException("Packaging Request Timed Out!")
            response = session.get(
                DOWNLOAD_URL.format(query_id=query_id),
                params={"format": "XML"},
                stream=True,
            )
            if not response.ok:
                print(response.request.url)
                print(response.status_code)
                print(response.text)
                raise HttpException("XML Download Failed!")

            with open(fname, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        self.objs = USApplicationXmlSet(fname, num_found)

    def fields(self):
        url = "https://ped.uspto.gov/api/search-fields"
        response = session.get(url)
        if response.ok:
            raw = response.json()
            output = {inflection.underscore(key): value for (key, value) in raw.items()}
            return output
        else:
            raise ValueError("Can't get fields!")


ns = dict(
    uspat="urn:us:gov:doc:uspto:patent",
    pat="http://www.wipo.int/standards/XMLSchema/ST96/Patent",
    uscom="urn:us:gov:doc:uspto:common",
    com="http://www.wipo.int/standards/XMLSchema/ST96/Common",
    xsi="http://www.w3.org/2001/XMLSchema-instance",
)


bib_data = dict(
    appl_id=".//uscom:ApplicationNumberText",
    app_filing_date=".//pat:FilingDate",
    app_type=".//uscom:ApplicationTypeCategory",
    app_cust_number=".//com:ContactText",
    app_group_art_unit=".//uscom:GroupArtUnitNumber",
    app_atty_dock_number=".//com:ApplicantFileReference",
    patent_title=".//pat:InventionTitle",
    app_status=".//uscom:ApplicationStatusCategory",
    app_status_date=".//uscom:ApplicationStatusDate",
    app_cls_subcls=".//pat:NationalSubclass",
    app_early_pub_date=".//uspat:PatentPublicationIdentification/com:PublicationDate",
    patent_number=".//uspat:PatentGrantIdentification/pat:PatentNumber",
    patent_issue_date=".//uspat:PatentGrantIdentification/pat:GrantDate",
    aia_status=".//uspat:FirstInventorToFileIndicator",
    app_entity_status=".//uscom:BusinessEntityStatusCategory",
    file_location=".//uscom:OfficialFileLocationCategory",
    file_location_date=".//uscom:OfficialFileLocationDate",
    app_examiner=".//pat:PrimaryExaminer//com:PersonFullName",
)


inv_data = dict(
    name="./com:PublicationContact/com:Name/com:PersonName",
    city="./com:PublicationContact/com:CityName",
    country="./com:PublicationContact/com:CountryCode",
    region="./com:PublicationContact/com:GeographicRegionName",
)

ph_data = dict(date="./uspat:RecordedDate", action="./uspat:CaseActionDescriptionText")

WHITESPACE_RE = re.compile("\s+")


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

class USApplicationXmlParser():

    def element_to_text(self, element):
        return WHITESPACE_RE.sub(" ", " ".join(element.itertext())).strip()


    def parse_element(self, element, data_dict):
        data = {
            key: self.element_to_text(element.find(value, ns))
            for (key, value) in data_dict.items()
            if element.find(value, ns) is not None
        }
        for key in data.keys():
            if "date" in key and data.get(key, False) != "-":
                data[key] = parse_dt(data[key]).date()
            elif data.get(key, False) == "-":
                data[key] = None
        return data


    def parse_bib_data(self, element):
        data = self.parse_element(element, bib_data)
        pub_no = element.find(
            ".//uspat:PatentPublicationIdentification/pat:PublicationNumber", ns
        )
        if pub_no is not None:
            if len(pub_no.text) > 7:
                pub_no = pub_no.text
            else:
                pub_no = str(data["app_early_pub_date"].year) + pub_no.text

            if len(pub_no) < 11:
                pub_no = pub_no[:4] + pub_no[4:].rjust(7, "0")

            kind_code = element.find(
                ".//uspat:PatentPublicationIdentification/com:PatentDocumentKindCode", ns
            )
            if kind_code is None:
                kind_code = ""
            else:
                kind_code = kind_code.text
            data["app_early_pub_number"] = pub_no + kind_code
        return data


    def parse_transaction_history(self, element):
        output = list()
        for event_el in element.findall(
            "./uspat:PatentRecord/uspat:ProsecutionHistoryData", ns
        ):
            event = self.parse_element(event_el, ph_data)
            event["action"], event["code"] = event["action"].rsplit(" , ", 1)
            output.append(event)
        return output


    def parse_inventors(self, element):
        output = list()
        for inv_el in element.findall(
            "./uspat:PatentRecord/uspat:PatentCaseMetadata/pat:PartyBag/pat:InventorBag/pat:Inventor",
            ns,
        ):
            data = self.parse_element(inv_el, inv_data)
            data["region_type"] = inv_el.find(
                "./com:PublicationContact/com:GeographicRegionName", ns
            ).attrib.get(
                "{http://www.wipo.int/standards/XMLSchema/ST96/Common}geographicRegionCategory",
                "",
            )
            output.append(data)
        return output


    def parse_applicants(self, element):
        output = list()
        for app_el in element.findall(
            "./uspat:PatentRecord/uspat:PatentCaseMetadata/pat:PartyBag/pat:ApplicantBag/pat:Applicant",
            ns,
        ):
            data = self.parse_element(app_el, inv_data)
            data["region_type"] = app_el.find(
                "./com:PublicationContact/com:GeographicRegionName", ns
            ).attrib.get(
                "{http://www.wipo.int/standards/XMLSchema/ST96/Common}geographicRegionCategory",
                "",
            )
            output.append(data)
        return output


    def case(self, element):
        return {
            **self.parse_bib_data(element),
            **dict(
                inventors=self.parse_inventors(element),
                transactions=self.parse_transaction_history(element),
                applicants=self.parse_applicants(element),
            ),
        }


    def xml_file(self, file_obj):
        try:
            for _, element in ET.iterparse(file_obj):
                if "PatentRecordBag" in element.tag:
                    yield element
        except ET.ParseError as e:
            print(e)


    def save_state(state):
        with open("pdb_state.json", "w") as f:
            json.dump(state, f, indent=2)


class USApplicationJsonSet(BaseSet):
    def __init__(self, data, length):
        self.data = data
        self._len = length
    
    def __len__(self):
        return self._len
    
    def __getitem__(self, key):
        for k, v in self.data[key].items():
            if 'date' in k and type(v) == str:
                self.data[key][k] = parse_dt(v).date()
        return USApplication(self.data[key])
        

class USApplicationXmlSet(BaseSet):
    parser = USApplicationXmlParser()

    def __init__(self, filename, length):
        self.filename = filename
        self._len = length
        self.cache = dict()
        self.zipfile = ZipFile(self.filename)
        self.files = self.zipfile.namelist()
        self.open_file = iter(list()) 
        self.counter = 0

    def __len__(self):
        return self._len

    def __getitem__(self, key):
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            if key < 0:
                key = len(self) - key

            if key not in self.cache:
                self.parse_item(key)
            return USApplication(self.cache[key])

    def parse_item(self, key):
        while self.counter <= key:
            try:
                tree = next(self.open_file)
                self.cache[self.counter] = self.parser.case(tree)
                self.counter += 1
            except StopIteration:
                self.open_file = self.parser.xml_file(self.zipfile.open(self.files.pop(0)))

class USApplication(Model):
    objects = USApplicationManager()
    trials = one_to_many('ip.PtabTrial', patent_number='patent_number')
    inpadoc = one_to_one('ip.Inpadoc', number='publication')

    @property
    def publication(self):
        if self.patent_number:
            return self.patent_number
        else:
            return self.app_early_pub_number
            
    def __repr__(self):
        return f'<USApplication(appl_id={self.appl_id})>'