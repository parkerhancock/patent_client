import json
import os
import re
import time
import warnings

from datetime import date, datetime
from zipfile import ZipFile

import inflection
import requests
from dateutil.parser import parse as parse_dt
from patent_client import CACHE_BASE
from patent_client.util import hash_dict
from patent_client.util import Manager
from patent_client.util import Model
from patent_client.util import one_to_many, one_to_one
from .xml_parser import USApplicationXmlParser


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
QUERY_FIELDS = "appEarlyPubNumber applId appLocation appType appStatus_txt appConfrNumber appCustNumber appGrpArtNumber appCls appSubCls appEntityStatus_txt patentNumber patentTitle primaryInventor firstNamedApplicant appExamName appExamPrefrdName appAttrDockNumber appPCTNumber appIntlPubNumber wipoEarlyPubNumber pctAppType firstInventorFile appClsSubCls rankAndInventorsList"

CACHE_DIR = CACHE_BASE / "uspto_examination_data"
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers["User-Agent"] = "python_patent_client"


class USApplicationManager(Manager):
    primary_key = "appl_id"

    def get_item(self, key):
        if not hasattr(self, "objs"):
            self.request()
        return self.objs[key]

    def __len__(self):
        if not hasattr(self, "_len"):
            self.request()
        return self._len

    def get(self, *args, **kwargs):
        if "publication" in kwargs:
            if "A1" in kwargs["publication"]:
                warnings.warn("Lookup by Publication does not work well")
                kwargs["app_early_pub_number"] = kwargs["publication"]
            else:
                kwargs["patent_number"] = kwargs["publication"][2:-2]
            del kwargs["publication"]
        manager = self.__class__(*args, **{**kwargs, **self.kwargs})
        count = manager.count()
        if count > 1:
            raise ValueError("More than one result!")
        elif count == 0:
            raise ValueError("Object Not Found!")
        else:
            return manager.first()

    def get_many(self, *args, **kwargs):
        manager = self.__class__(
            *args, **{**kwargs, **self.kwargs, **dict(default_connector="OR")}
        )
        return manager

    def _generate_query(self, params=dict()):
        params = {**self.filter_params, **dict(sort=self.sort_params), **params}
        if "default_connector" in params:
            del params["default_connector"]
        sort_query = ""

        if "sort" in params:
            for s in params["sort"]:
                if s[0] == "-":
                    sort_query += f"{inflection.camelize(s[1:], uppercase_first_letter=False)} desc "
                else:
                    sort_query += (
                        f"{inflection.camelize(s, uppercase_first_letter=False)} asc"
                    )

            del params["sort"]

        query = ""
        mm_active = True
        for k, v in params.items():
            field = inflection.camelize(k, uppercase_first_letter=False)
            if not v:
                continue
            elif type(v) in (list, tuple):
                body = f" OR ".join(v)
                mm_active = False
            else:
                body = v
            query += f"{field}:({body}) "

        mm = "100%" if "appEarlyPubNumber" not in query else "90%"

        query = {
            "qf": QUERY_FIELDS,
            "fl": "*",
            "searchText": query.strip(),
            "sort": sort_query.strip(),
            "facet": "false",
            "mm": mm,
        }
        if not mm_active:
            del query['mm']
        return query

    def request(self, params=dict()):
        query_params = self._generate_query(params)
        fname = hash_dict(query_params) + ".json"
        fname = os.path.join(CACHE_DIR, fname)
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
        num_found = results["numFound"]
        self._len = num_found
        if num_found <= 20:
            with open(fname, "w") as f:
                json.dump(data, f, indent=2)
            self.objs = USApplicationJsonSet(results["docs"], num_found)
        else:
            return self._package_xml(query_params, data)

    def _package_xml(self, query_params, data):
        fname = hash_dict(query_params) + ".zip"
        fname = os.path.join(CACHE_DIR, fname)
        query_id = data["queryId"]
        results = data["queryResults"]["searchResponse"]["response"]
        num_found = results["numFound"]
        if not os.path.exists(fname):
            time.sleep(0.5)
            response = session.put(
                PACKAGE_URL.format(query_id=query_id), params={"format": "XML"}
            )
            if not response.ok:
                raise HttpException(f"Packaging Request Failed!\n{response.request.url}\n{response.status_code}\n{response.text}")

            start = time.time()
            while time.time() - start < 600:
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
                raise HttpException(f"XML Download Failed!\n{response.request.url}\n{response.status_code}\n{response.text}")

            with open(fname, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        self.objs = USApplicationXmlSet(fname, num_found)

    @property
    def fields(self):
        url = "https://ped.uspto.gov/api/search-fields"
        response = session.get(url)
        if response.ok:
            raw = response.json()
            output = {inflection.underscore(key): value for (key, value) in raw.items()}
            return output
        else:
            raise ValueError("Can't get fields!")

    @property
    def query_fields(self):
        fields = self.fields
        for k in sorted(fields.keys()):
            if 'facet' in k:
                continue
            print(f"{k} ({fields[k]})")

class USApplication(Model):
    """
    US Application
    ==============
    This object wraps a US Application obtained from the Patent Examination Data System (https://peds.uspto.gov)
    
    -------------------------
    To Fetch a US Application
    -------------------------
    The main way to create a US Application is by querying the US Application manager at USApplication.objects

        USApplication.objects.filter(query) -> obtains multiple matching applications
        USApplication.objects.get(query) -> obtains a single matching application, errors if more than one is retreived

    The query can either be a single number, which is treated like an application number, or a keyword argument:
    
        USApplication.objects.get("15123456") -> Retreives US Application # 15123456
        USApplication.objects.get(patent_number="6103599") -> Retreives the US Application which issued as US Patent 6103599

    All arguments can be specified multiple times:
    
        USApplication.objects.get("15123456", "15123457") -> Retreives US Applications 15123456 and 15123457
        USApplication.objects.get(patent_number=['6103599', '6103600']) -> Retreives the US Applications which issued as US Patents 6103599 and 6103600

    NOTE: All keyword arguments are repeated by placing them in a list, but application numbers can be repeated as non-keyword arguments

    Date queries are made as strings in ISO format - YYYY-MM-DD (e.g. 2019-02-01 for Feb. 1, 2019)
    
    The complete list of available query fields is at USApplication.objects.fields

    --------------
    Using the Data
    --------------
    Data retreived from the US Patent Examination Data System is populated as attributes on the US Application object.
    A complete list of available fields is at USApplication.attrs. All the data can be retreived as a Python dictionary
    by calling USApplication.dict()

    There are also several composite data types available from a US Application, including:

        app.transaction_history -> list of transactions (filings, USPTO actions, etc.) involving the application
        app.children -> list of child applications
        app.parents -> list of parent applications
        app.pta_pte_history -> Patent Term Adjustment / Extension Event History
        app.pta_pte_summary -> Patent Term Adjustment / Extension Results, including total term extension
        app.correspondent -> Contact information for prosecuting law firm
        app.attorneys -> List of attorneys authorized to take action in the case

    Each of these also attaches data as attributes to the objects, and implements a .dict() method.

    ------------
    Related Data
    ------------
    A US Application is also linked to other resources avaialble through patent_client, including:
    
        app.trials -> list of PTAB trials involving this application
        app.inpadoc -> list to corresponding INPADOC objects (1 for each publication)
            HINT: inpadoc family can be found at app.inpadoc[0].family
        app.assignments -> list of assignments that mention this application

    Also, related US Applications can be obtained through their relationship:

    app.children[0].application -> a new USApplication object for the first child. 

    """
    objects = USApplicationManager()
    trials = one_to_many("patent_client.PtabTrial", patent_number="patent_number")
    inpadoc = one_to_many("patent_client.Inpadoc", number="appl_id")
    assignments = one_to_many("patent_client.Assignment", appl_id="appl_id")
    attrs =['appl_id', 'applicants', 'app_filing_date', 'app_exam_name', 
    'inventor_name', 'inventors', 'app_early_pub_number', 'app_early_pub_date', 
    'app_location', 'app_grp_art_number', 'patent_number', 'patent_issue_date', 
    'app_status', 'app_status_date', 'patent_title', 'app_attr_dock_number', 
    'first_inventor_file', 'app_type', 'app_cust_number', 'app_cls_sub_cls', 
    'corr_addr_cust_no', 'app_entity_status', 'app_confr_number']

    @property
    def publication(self):
        if self.patent_number:
            return "US" + self.patent_number
        else:
            return self.app_early_pub_number

    @property
    def transaction_history(self):
       return list(sorted((Transaction(d) for d in self.data.get('transactions', list())), key=lambda x: x.date)) 

    @property
    def children(self):
        return [Relationship(d) for d in self.data.get('child_continuity', list())]
    
    @property
    def parents(self):
        return [Relationship(d) for d in self.data.get('parent_continuity', list())]

    @property
    def pta_pte_history(self):
        return list(sorted((PtaPteHistory(d) for d in self.data.get('pta_pte_tran_history', list())), key=lambda x: x.number))

    @property
    def pta_pte_summary(self):
        return PtaPteSummary(self.data)

    @property
    def correspondent(self):
        return Correspondent(self.data)

    @property
    def attorneys(self):
        return list(Attorney(d) for d in self.data.get('attrny_addr', list()))

    def __repr__(self):
        return f"<USApplication(appl_id={self.appl_id})>"

class Relationship(Model):
    application = one_to_one("patent_client.USApplication", appl_id='appl_id')
    attrs = ['appl_id', 'filing_date', 'patent_number', 'status', 'relationship', 'aia']

    def __init__(self, *args, **kwargs):
        super(Relationship, self).__init__(*args, **kwargs)
        data = self.data
        self.appl_id = data['claim_application_number_text']
        self.filing_date = data['filing_date']
        self.patent_number = data.get('patent_number_text', None) or None
        self.status = data['application_status']
        self.relationship = data['application_status_description'].replace('This application ', '')
        self.aia = data['aia_indicator'] == 'Y'

class PtaPteHistory(Model):
    attrs = ['number', 'date', 'description', 'pto_days', 'applicant_days', 'start']

    def __init__(self, *args, **kwargs):
        super(PtaPteHistory, self).__init__(*args, **kwargs)
        data = self.data
        self.number = float(data['number'])
        self.date = data['pta_or_pte_date']
        self.description = data['contents_description']
        self.pto_days = float(data['pto_days'] or 0)
        self.applicant_days = float(data['appl_days'] or 0)
        self.start = float(data['start'])

class PtaPteSummary(Model):
    attrs = ['type', 'a_delay', 'b_delay', 'c_delay', 'overlap_delay', 'pto_delay', 'applicant_delay', 'pto_adjustments', 'total_days']

    def __init__(self, data):
        self.type = data['pta_pte_ind']
        self.pto_adjustments = int(data['pto_adjustments'])
        self.overlap_delay = int(data['overlap_delay'])
        self.a_delay = int(data['a_delay'])
        self.b_delay = int(data['b_delay'])
        self.c_delay = int(data['c_delay'])
        self.pto_delay = int(data['pto_delay'])
        self.applicant_delay = int(data['appl_delay'])
        self.total_days = int(data['total_pto_days'])

class Transaction(Model):
    attrs = ['date', 'code', 'description']

    def __init__(self, data):
        self.date = datetime.strptime(data['recordDate'][:10], '%Y-%m-%d').date()
        self.code = data['code']
        self.description = data['description']

class Correspondent(Model):
    attrs = ['name_line_one', 'name_line_two', 'cust_no', 'street_line_one', 'street_line_two', 'street_line_three', 'city', 'geo_region_code', 'postal_code']

    def __init__(self, data):
        for k, v in data.items():
            if 'corr' == k[:4]:
                key = k.replace('corr_addr_', '')
                setattr(self, key, v)

class Attorney(Model):
    attrs = ['registration_no', 'full_name', 'phone_num', 'reg_status']

class USApplicationXmlSet(Manager):
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
                self.open_file = self.parser.xml_file(
                    self.zipfile.open(self.files.pop(0))
                )

class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

class USApplicationJsonSet(Manager):
    def __init__(self, data, length):
        self.data = data
        self._len = length

    def __len__(self):
        return self._len

    def __getitem__(self, key):
        for k, v in self.data[key].items():
            if "date" in k and type(v) == str:
                self.data[key][k] = parse_dt(v).date()
        return USApplication(self.data[key])
