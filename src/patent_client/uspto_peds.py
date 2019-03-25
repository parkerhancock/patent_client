import json
import os
import re
import time
import warnings

from datetime import date, datetime
from zipfile import ZipFile
from dateutil.relativedelta import relativedelta

import inflection
import requests
from dateutil.parser import parse as parse_dt
from patent_client import CACHE_BASE, TEST_BASE
from patent_client.util import hash_dict
from patent_client.util import Manager
from patent_client.util import Model
from patent_client.util import one_to_many, one_to_one


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

TEST_DIR = TEST_BASE / "uspto_examination_data"
TEST_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers["User-Agent"] = "python_patent_client"

class USApplicationManager(Manager):
    primary_key = "appl_id"

    def __init__(self, *args, **kwargs):
        super(USApplicationManager, self).__init__(*args, **kwargs)
        self.pages = dict()
    
    def get_item(self, key):
        page_number = int(key / 20)
        page_position = key % 20
        return USApplication(self.get_page(page_number)['docs'][page_position])
    
    def __len__(self):
        return self.get_page(0)["numFound"]
    
    def get_page(self, page_number):
        if page_number not in self.pages:
            query_params = self.query_params(page_number)
            fname = hash_dict(query_params) + ".json"
            if self.test_mode:
                fname = os.path.join(TEST_DIR, fname)
            else:
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
                with open(fname, "w") as f:
                    json.dump(data, f, indent=2)
            else:
                data = json.load(open(fname))
            self.pages[page_number] = data["queryResults"]["searchResponse"]["response"]
        return self.pages[page_number]
        #num_found = results["numFound"]
        #self._len = num_found
        #if num_found > 20 or self.config['options'].get('force_xml', True):
        #    return self._package_xml(query_params, data)
        #self.objs = USApplicationJsonSet(results["docs"], num_found)

    def query_params(self, page_no):
        sort_query = ""
        for s in self.config['order_by']:
            if s[0] == "-":
                sort_query += f"{inflection.camelize(s[1:], uppercase_first_letter=False)} desc "
            else:
                sort_query += (
                    f"{inflection.camelize(s, uppercase_first_letter=False)} asc"
                )

        query = ""
        mm_active = True
        for k, v in self.config['filter'].items():
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
            "start": page_no * 20,
            "rows": 20,
        }
        if not mm_active:
            del query['mm']
        return query
        
    @property
    def allowed_filters(self):
        fields = self.fields()
        return list(fields.keys())

    def fields(self):
        if not hasattr(self.__class__, '_fields'):
            url = "https://ped.uspto.gov/api/search-fields"
            response = session.get(url)
            if not response.ok:
                raise ValueError("Can't get fields!")
            
            raw = response.json()
            output = {inflection.underscore(key): value for (key, value) in raw.items()}
            self.__class__._fields = output
        return self.__class__._fields
    
    @property
    def query_fields(self):
        fields = self.fields()
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
        app.expiration -> Patent Expiration Data (earliest non-provisional US parent + 20 years + extension and a flag for the presnce of a Terminal Disclaimer)

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
    'inventors', 'app_early_pub_number', 'app_early_pub_date', 
    'app_location', 'app_grp_art_number', 'patent_number', 'patent_issue_date', 
    'app_status', 'app_status_date', 'patent_title', 'app_attr_dock_number', 
    'first_inventor_file', 'app_type', 'app_cust_number', 'app_cls_sub_cls', 
    'corr_addr_cust_no', 'app_entity_status', 'app_confr_number', 'transaction_history',
    'children', 'parents', 'foreign_priority_applications', 'pta_pte_history', 'pta_pte_summary', 'correspondent', 
    'attorneys']

    @property
    def publication(self):
        if self.patent_number:
            return "US" + self.patent_number
        else:
            return self.app_early_pub_number

    @property
    def kind(self):
        if "PCT" in self.appl_id:
            return "PCT"
        if self.appl_id[0] == "6":
            return "Provisional"
        return "Nonprovisional"

    @property
    def expiration(self):
        expiration_data = dict()
        term_parents = [p for p in self.parents 
                    if p.relationship not in [
                        'Claims Priority from Provisional Application',
                        'is a Reissue of'
                    ]]
        if term_parents:
            term_parent = sorted(term_parents, key=lambda x: x.parent_app_filing_date)[0]
            relationship = term_parent.relationship
            parent_filing_date = term_parent.parent_app_filing_date
            term_parent_app = term_parent.parent
        else:
            relationship = "self"
            term_parent_app = self
            parent_filing_date = self.app_filing_date

        
        expiration_data['parent_appl_id'] = term_parent_app.appl_id
        expiration_data['parent_app_filing_date'] = parent_filing_date
        expiration_data['parent_relationship'] = relationship
        expiration_data['20_year_term'] = parent_filing_date + relativedelta(years=20)
        expiration_data['pta_or_pte'] = self.pta_pte_summary.total_days
        expiration_data['extended_term'] = expiration_data['20_year_term'] + relativedelta(days=expiration_data['pta_or_pte'])

        transactions = self.transaction_history
        try:
            disclaimer = next(t for t in transactions if t.code == 'DIST')
            expiration_data['terminal_disclaimer_filed'] = True
        except StopIteration:
            expiration_data['terminal_disclaimer_filed'] = False 

        return expiration_data

    @property
    def transaction_history(self):
       return list(sorted((Transaction(d) for d in self.data.get('transactions', list())), key=lambda x: x.date)) 

    @property
    def children(self):
        return [Relationship(d, base_app=self) for d in self.data.get('child_continuity', list())]
    
    @property
    def parents(self):
        return [Relationship(d, base_app=self) for d in self.data.get('parent_continuity', list())]

    @property
    def foreign_priority_applications(self):
        return [ForeignPriority(d) for d in self.data.get('foreign_priority', list())]

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
    parent = one_to_one("patent_client.USApplication", appl_id='parent_appl_id')
    child = one_to_one("patent_client.USApplication", appl_id='child_appl_id')
    attrs = ['appl_id', 'filing_date', 'patent_number', 'status', 'relationship', 'related_to_appl_id']


    def __init__(self, *args, **kwargs):
        super(Relationship, self).__init__(*args, **kwargs)
        data = self.data
        self.relationship = data['application_status_description'].replace('This application ', '')
        if self.relationship == "claims the benefit of":
            self.parent_appl_id = data.get('application_number_text', None)
            self.child_appl_id = data['claim_application_number_text']
            self.parent_app_filing_date = None
        else:
            self.child_appl_id = data.get('application_number_text', None)
            self.parent_appl_id = data['claim_application_number_text']
            self.parent_app_filing_date = data['filing_date']
            
            # Following attibutes removed in the switch to clearly identifyign a parent and child
            #self.related_to_appl_id = kwargs['base_app'].appl_id
            
            #self.parent_patent_number = data.get('patent_number_text', None) or None
            #self.parent_status = data.get('application_status', None)
            #self.relationship = data['application_status_description'].replace('This application ', '')
            #self.aia = data['aia_indicator'] == 'Y'

    def __repr__(self):
        return f"<Relationship(child={self.child_appl_id}, relationship={self.relationship}, parent={self.parent_appl_id})>"


class ForeignPriority(Model):
    attrs = ['country_name', 'application_number_text', 'filing_date']

    def __repr__(self):
        return f"<ForeignPriority(country_name={self.country_name}, application_number_text={self.application_number_text})"

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
        try:
            self.total_days = int(data['total_pto_days'])
        except KeyError:
            self.total_days = 0
            self.type = None
            self.pto_adjustments = 0
            self.overlap_delay = 0
            self.a_delay = 0
            self.b_delay = 0
            self.c_delay = 0
            self.pto_delay = 0
            self.applicant_delay = 0
            return
        self.type = data.get('pta_pte_ind', None)
        self.pto_adjustments = int(data['pto_adjustments'])
        self.overlap_delay = int(data['overlap_delay'])
        self.a_delay = int(data['a_delay'])
        self.b_delay = int(data['b_delay'])
        self.c_delay = int(data['c_delay'])
        self.pto_delay = int(data['pto_delay'])
        self.applicant_delay = int(data['appl_delay'])
        

class Transaction(Model):
    attrs = ['date', 'code', 'description']

    def __init__(self, data):
        self.date = data['record_date']
        self.code = data['code']
        self.description = data['description']

    def __repr__(self):
        return f'<Transaction(date={self.date.isoformat()}, description={self.description})>'

class Correspondent(Model):
    attrs = ['name_line_one', 'name_line_two', 'cust_no', 'street_line_one', 'street_line_two', 'street_line_three', 'city', 'geo_region_code', 'postal_code']

    def __init__(self, data):
        for k, v in data.items():
            if 'corr' == k[:4]:
                key = k.replace('corr_addr_', '')
                setattr(self, key, v)

class Attorney(Model):
    attrs = ['registration_no', 'full_name', 'phone_num', 'reg_status']


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
