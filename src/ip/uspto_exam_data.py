import json
import os
import time
from hashlib import sha1

from zipfile import ZipFile
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from datetime import date
from dateutil.parser import parse as parse_date
import json
import re
import os

import inflection
import requests

from ip import CACHE_BASE

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
CACHE_DIR = CACHE_BASE / 'uspto_examination_data'
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers["User-Agent"] = "python-ip"


class USApplicationManager():
    def is_available():
        query = {}
        try:
            result = PatExData.get_by_application_number(application_number=15145443)
        except NotAvailableException as e:
            return False
        return True

    def get(self, *args, **kwargs):
        query = self._generate_query(*args, **kwargs)
        result = self._submit(query)
        if not result:
            raise ValueError("No Matches Found!")
        if len(result) > 1:
            raise ValueError("Multiple Matches Found!")
        return result[0]

    def bulk_get(self, *args, **kwargs):
        if args:
            return self.bulk_get(appl_id=args[0])
        output = list()
        for keyword, query_list in kwargs.items():
            query_string = list()
            for num in query_list:
                query_string.append(num)
            output += self._submit(
                {
                    "qf": inflection.camelize(keyword, uppercase_first_letter=False),
                    "searchText": " ".join(query_string),
                    "facet": "false",
                }
            )
        return output

    def search(self, *args, **kwargs):
        query = self._generate_query(*args, **kwargs)
        return self._submit(query)

    def _generate_query(self, *args, **kwargs):
        if args:
            kwargs["appl_id"] = args[0]
        if len(kwargs) > 1:
            return NotImplementedError("Can't get on more than one field!")
        if not args and not kwargs:
            raise TypeError("No Valid Argument Passed!")

        qf = list(kwargs.keys())[0]
        searchText = kwargs[qf]
        if type(searchText) == list:
            searchText = " ".join(str(item) for item in searchText)
        return {
            "qf": inflection.camelize(qf, False),
            "searchText": searchText,
            "facet": "false",
            "mm": "100%",
        }

    def fields(self):
        url = "https://ped.uspto.gov/api/search-fields"
        response = session.get(url)
        if response.ok:
            raw = response.json()
            output = {inflection.underscore(key): value for (key, value) in raw.items()}
            return output
        else:
            raise ValueError("Can't get fields!")



    def _submit(self, query):
        qstring = "".join([str(k) + str(query[k]) for k in sorted(query.keys())])
        fname = str(sha1(qstring.encode("utf-8")).hexdigest()) + ".json"
        fname = os.path.join(CACHE_DIR, fname)
        if not os.path.exists(fname):
            response = session.post(QUERY_URL, json=query)
            print(response.request.body.decode("utf-8"))
            if not response.ok:
                if "requested resource is not available" in response.text:
                    raise NotAvailableException("Patent Examination Data is Offline")
                else:
                    raise HttpException(
                        f"{response.status_code}\n{response.text}\n{response.headers}"
                    )
            with open(fname, 'w') as f:
                json.dump(response.json(), f, indent=2)

        data = json.load(open(fname))
        results = data["queryResults"]["searchResponse"]["response"]
        num_found = results['numFound']
        if num_found <= 20:
            return USApplicationJsonSet(results['docs'], num_found)
        else:
            return self._package_xml(query, data)
    
    def _package_xml(self, query, data):
        qstring = "".join([str(k) + str(query[k]) for k in sorted(query.keys())])
        fname = str(sha1(qstring.encode("utf-8")).hexdigest()) + ".zip"
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
        return USApplicationXmlSet(fname, num_found)

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

    def element_to_text(element):
        return WHITESPACE_RE.sub(" ", " ".join(element.itertext())).strip()


    def parse_element(element, data_dict):
        data = {
            key: element_to_text(element.find(value, ns))
            for (key, value) in data_dict.items()
            if element.find(value, ns) is not None
        }
        for key in data.keys():
            if "date" in key and data.get(key, False) != "-":
                data[key] = parse_date(data[key]).date()
            elif data.get(key, False) == "-":
                data[key] = None
        return data


    def parse_bib_data(element):
        data = parse_element(element, bib_data)
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


    def parse_transaction_history(element):
        output = list()
        for event_el in element.findall(
            "./uspat:PatentRecord/uspat:ProsecutionHistoryData", ns
        ):
            event = parse_element(event_el, ph_data)
            event["action"], event["code"] = event["action"].rsplit(" , ", 1)
            output.append(event)
        return output


    def parse_inventors(element):
        output = list()
        for inv_el in element.findall(
            "./uspat:PatentRecord/uspat:PatentCaseMetadata/pat:PartyBag/pat:InventorBag/pat:Inventor",
            ns,
        ):
            data = parse_element(inv_el, inv_data)
            data["region_type"] = inv_el.find(
                "./com:PublicationContact/com:GeographicRegionName", ns
            ).attrib.get(
                "{http://www.wipo.int/standards/XMLSchema/ST96/Common}geographicRegionCategory",
                "",
            )
            output.append(data)
        return output


    def parse_applicants(element):
        output = list()
        for app_el in element.findall(
            "./uspat:PatentRecord/uspat:PatentCaseMetadata/pat:PartyBag/pat:ApplicantBag/pat:Applicant",
            ns,
        ):
            data = parse_element(app_el, inv_data)
            data["region_type"] = app_el.find(
                "./com:PublicationContact/com:GeographicRegionName", ns
            ).attrib.get(
                "{http://www.wipo.int/standards/XMLSchema/ST96/Common}geographicRegionCategory",
                "",
            )
            output.append(data)
        return output


    def parse_case(element):
        return {
            **parse_bib_data(element),
            **dict(
                inventors=parse_inventors(element),
                transactions=parse_transaction_history(element),
                applicants=parse_applicants(element),
            ),
        }


    def parse_xml_file(file_obj):
        try:
            for _, element in ET.iterparse(file_obj):
                if "PatentRecordBag" in element.tag:
                    yield element
        except ET.ParseError as e:
            print(e)


    def save_state(state):
        with open("pdb_state.json", "w") as f:
            json.dump(state, f, indent=2)


class USApplicationJsonSet:
    def __init__(self, data, length):
        self.data = data
        self._len = length
    
    def __len__(self):
        return self._len
    
    def __getitem__(self, key):
        return USApplication(self.data[key])

class USApplicationXmlSet:
    parser = USApplicationXmlParser()

    def __init__(self, filename, length):
        self.filename = filename
        self._len = length
        self.cache = dict()
        self.zipfile = ZipFile(self.filename)
        self.files = self.zipfile.namelist()
        self.open_file = list() 
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
            return UsApplication(self.cache[key])

    def parse_item(self, key):
        while self.counter <= key:
            try:
                tree = next(self.open_file)
                self.cache[self.counter] = self.parser.case()
                self.counter += 1
            except StopIteration:
                self.open_file = parse_xml_file(self.zipfile.open(self.files.pop(0)))

class USApplication():
    objects = USApplicationManager()

    def __init__(self, data):
        self.dict = data
        for k, v in data.items():
            setattr(self, inflection.underscore(k), v)