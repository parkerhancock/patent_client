import math
import re
import xml.etree.ElementTree as ET

import requests

# USPTO has a malconfigured SSL connection. Suppress warnings about it.
import urllib3
from dateutil.parser import parse as parse_date
from inflection import underscore
from patent_client import CACHE_BASE
from patent_client.util import Manager
from patent_client.util import Model

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOOKUP_URL = "https://assignment-api.uspto.gov/patent/lookup"

NUMBER_CLEAN_RE = re.compile("[^\d]")
CACHE_DIR = CACHE_BASE / "uspto_assignment"
CACHE_DIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers = {"Accept": "application/xml"}


class AssignmentParser:
    def doc(self, element):
        data = self.xml_to_dict(element)
        data[
            "image_url"
        ] = f'http://legacy-assignments.uspto.gov/assignments/assignment-pat-{data["display_id"]}.pdf'
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


class AssignmentManager(Manager):
    parser = AssignmentParser()
    rows = 50
    obj_class = "patent_client.uspto_assignments.Assignment"

    def __init__(self, *args, **kwargs):
        super(AssignmentManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    def __repr__(self):
        return f"<AssignmentManager>"

    def get_item(self, key):
        if key < 0:
            key = len(self) - key
        page_no = math.floor(key / self.rows)
        offset = key - page_no * self.rows
        return Assignment(self._get_page(page_no)[offset])

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
            "publication": "PublicationNumber",
            "assignee": "OwnerName",
            "assignor": "PriorOwnerName",
            "pct_application": "PCTNumber",
            "correspondent": "CorrespondentName",
            "reel_frame": "ReelFrame",
        }
        for key, value in kwargs.items():
            field = fields[key]
            query = value
        if field in ["PatentNumber", "ApplicationNumber"]:
            query = NUMBER_CLEAN_RE.sub("", str(query))

        return self.__class__(
            *self.args,
            **{**self.kwargs, **dict(filter__query=query, filter__field=field)},
        )

    def __len__(self):
        if not hasattr(self, "_len"):
            self._get_page(0)
        return self._len

    def _get_page(self, page_no):
        if page_no not in self.pages:
            field = self.kwargs["filter__field"]
            query = self.kwargs["filter__query"]
            params = {
                "filter": field,
                "query": query,
                "rows": self.rows,
                "offset": page_no * self.rows,
            }
            filename = "-".join(
                [field, query, str(self.rows), str(page_no * self.rows), ".xml"]
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
        tree = ET.fromstring(text.encode("utf-8"))
        result = tree.find("./result")
        self._len = int(result.attrib["numFound"])
        return [self.parser.doc(doc) for doc in result]


class Assignment(Model):
    objects = AssignmentManager()

    def __repr__(self):
        return f"<Assignment(id={self.id})>"
