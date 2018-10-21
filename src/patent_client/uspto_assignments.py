import math
import os
import time
import re
import warnings
import xml.etree.ElementTree as ET
from datetime import date as date_obj
from itertools import chain
from dateutil.parser import parse as parse_date
from inflection import underscore
import requests


from ip import CACHE_BASE
from ip.util import BaseSet, Model

# USPTO has a malconfigured SSL connection. Suppress warnings about it.
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOOKUP_URL = "https://assignment-api.uspto.gov/patent/lookup"

NUMBER_CLEAN_RE = re.compile("[^\d]")
CACHE_DIR = CACHE_BASE / "uspto_assignment"
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers = {"Accept": "application/xml"}

class AssignmentManager:

    def filter(self, **kwargs):
        """Get assignments. 
        Args:
            patent: pat no to search
            application: app no to search
            assignee: assignee name to search
        """
        fields = {
            "patent": "PatentNumber",
            "application": "ApplicationNumber",
            "assignee": "OwnerName",
            "assignor": "PriorOwnerName",
            "pct_application": "PCTNumber",
            "correspondent": "CorrespondentName",
            "reel_frame": "ReelFrame"
        }
        for key, value in kwargs.items():
            field = fields[key]
            query = value
        if field in ["PatentNumber", "ApplicationNumber"]:
            query = NUMBER_CLEAN_RE.sub("", str(query))

        return AssignmentSet(field, query)

class AssignmentParser():
    def doc(self, element):
        data = self.xml_to_dict(element)
        data['image_url'] = f'http://legacy-assignments.uspto.gov/assignments/assignment-pat-{data["display_id"]}.pdf'
        return data

    def xml_to_list(self, element):
        output = list()
        for el in list(element):
            output.append(self.xml_to_pytype(el))
        if len(output) == 1:
            output = output[0]
        return output


    def xml_to_pytype(self, element):
        if element.text == "NULL":
            return None
        elif element.tag == "str":
            return element.text
        elif element.tag == "date":
            # To ensure the result is JSON-serializable, convert to isoformat
            date = parse_date(element.text).date()
            if date < parse_date("1776-01-01").date():
                return None
            return date.isoformat()
        elif element.tag == "int" or element.tag == "long":
            return int(element.text)


    def xml_to_dict(self, element):
        output = dict()
        for el in list(element):
            key = el.attrib["name"]
            key = underscore(key)
            if el.tag == "arr" or el.tag == "lst":
                value = self.xml_to_list(el)
            else:
                value = self.xml_to_pytype(el)
            output[key] = value
        return output


class AssignmentSet(BaseSet):
    parser = AssignmentParser()
    rows = 50

    def __init__(self, field, query):
        self.field = field
        self.query = query
        self.pages = dict()

    def __repr__(self):
        return f'<AssignmentSet>'

    def __getitem__(self, key):
        if type(key) == slice:
            indices = list(range(len(self)))[key.start : key.stop : key.step]
            return [self.__getitem__(index) for index in indices]
        else:
            if key < 0:
                key = len(self) - key
            page_no = math.floor(key / self.rows)
            offset = key - page_no * self.rows
            return Assignment(self._get_page(page_no)[offset])

    def __len__(self):
        if not hasattr(self, "_len"):
            self._get_page(0)
        return self._len

    def _get_page(self, page_no):
        if page_no not in self.pages:
            params = {
                "filter": self.field,
                "query": self.query,
                "rows": self.rows,
                "offset": page_no * self.rows,
            }
            filename = "-".join(
                [self.field, self.query, str(self.rows), str(page_no * self.rows), ".xml"]
            ).replace("/", "_")
            filename = CACHE_DIR / filename
            if filename.exists():
                text = open(filename).read()
            else:
                response = session.get(LOOKUP_URL, params=params, verify=False)
                text = response.text
                with open(filename, "w") as f:
                    f.write(text)

            self.pages[page_no] = self._parse_page(text)
        return self.pages[page_no]
    
    def _parse_page(self, text):
        tree = ET.fromstring(text.encode('utf-8'))
        result = tree.find('./result')
        self._len = int(result.attrib['numFound'])
        return [self.parser.doc(doc) for doc in result]

class Assignment(Model):
    objects = AssignmentManager()

    def __repr__(self):
        return f'<Assignment(id={self.id})>'