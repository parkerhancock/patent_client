import math
import re
import xml.etree.ElementTree as ET

import requests
import urllib3
from dateutil.parser import parse as parse_date
from inflection import underscore
from patent_client import CACHE_BASE, TEST_BASE
from patent_client.util import Manager
from patent_client.util import Model, one_to_many, one_to_one
from patent_client.util import hash_dict
import datetime


# USPTO has a malconfigured SSL connection. Suppress warnings about it.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOOKUP_URL = "https://assignment-api.uspto.gov/patent/lookup"

NUMBER_CLEAN_RE = re.compile(r"[^\d]")
CACHE_DIR = CACHE_BASE / "uspto_assignment"
CACHE_DIR.mkdir(exist_ok=True)
TEST_DIR = TEST_BASE / "uspto_assignment"
TEST_DIR.mkdir(exist_ok=True)


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
    fields = {
        "patent_number": "PatentNumber",
        "appl_id": "ApplicationNumber",
        "app_early_pub_number": "PublicationNumber",
        "assignee": "OwnerName",
        "assignor": "PriorOwnerName",
        "pct_number": "PCTNumber",
        "correspondent": "CorrespondentName",
        "id": "ReelFrame",
    }
    parser = AssignmentParser()
    rows = 50
    obj_class = "patent_client.uspto_assignments.Assignment"
    primary_key = "id"

    def __init__(self, *args, **kwargs):
        super(AssignmentManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    def __repr__(self):
        return f"<AssignmentManager>"

    @property
    def allowed_filters(self):
        return list(self.fields.keys())

    def get_item(self, key):
        if key < 0:
            key = len(self) - key
        page_no = math.floor(key / self.rows)
        offset = key - page_no * self.rows
        return Assignment(self._get_page(page_no)[offset])

    def get_query(self, page_no):
        """Get assignments. 
        Args:
            patent: pat no to search
            application: app no to search
            assignee: assignee name to search
        """

        for key, value in self.config['filter'].items():
            field = self.fields[key]
            query = value
        if field in ["PatentNumber", "ApplicationNumber"]:
            query = NUMBER_CLEAN_RE.sub("", str(query))

        sort = list()
        for p in self.config['order_by']:
            if sort[0] == "-":
                sort.append(p[1:] + "+desc")
            else:
                sort.append(p + "+asc")

        return {
            "filter": field,
            "query": query,
            "rows": self.rows,
            "offset": page_no * self.rows,
            "sort": " ".join(sort),
        }

    def __len__(self):
        if not hasattr(self, "_len"):
            self._get_page(0)
        return self._len

    def _get_page(self, page_no):
        if page_no not in self.pages:
            params = self.get_query(page_no)
            #import pdb; pdb.set_trace()
            filename = "-".join(
                [
                    hash_dict(params),
                    str(self.rows),
                    str(page_no * self.rows),
                    ".xml",
                ]
            ).replace("/", "_")
            if self.test_mode:
                filename = TEST_DIR / filename
            else:
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

    @property
    def query_fields(self):
        fields = self.fields
        for k in sorted(fields.keys()):
            print(k)


class Assignment(Model):
    """
    Assignments
    ===========
    This object wraps the USPTO Assignment API (https://assignments.uspto.gov)

    ----------------------
    To Fetch an Assignment
    ----------------------
    The main way to create an Assignment is by querying the Assignment manager at Assignment.objects

    Assignment.objects.filter(query) -> obtains multiple matching applications
    Assignment.objects.get(query) -> obtains a single matching application, errors if more than one is retreived

    The query can either be a single number, which is treated as a reel/frame number (e.g. "123-1321"), or a keyword.
    Available query types are: 
        patent_number, 
        appl_id (application #), 
        app_early_pub_number (publication #), 
        assignee,
        assignor,
        pct_number (PCT application #),
        correspondent,
        reel_frame

    --------------
    Using the Data
    --------------
    An Assignment object has the following properties:
        id (reel/frame #)
        attorney_dock_num
        conveyance_text
        last_update_date
        page_count
        recorded_date
        correspondent
        assignees
        assignors
        properties

    Additionally, the original assignment document can be downloaded to the working directory by calling:

    assignment.download()
    
    ------------
    Related Data
    ------------
    An Assignment is also linked to other resources available through patent_client. 
    A list of all assigned applications is available at:

    assignment.us_applications

    Additionally, each property entry in properties links to the corresponding application at:

    assignment.properties[0].us_application


    """

    primary_key = "reel_frame"
    attrs = [
        "id",
        "attorney_dock_num",
        "conveyance_text",
        "last_update_date",
        "page_count",
        "recorded_date",
        "correspondent",
        "assignors",
        "assignees",
        "properties",
        "image_url",
    ]
    objects = AssignmentManager()
    us_applications = one_to_many("patent_client.USApplication", appl_id="appl_num")

    def __repr__(self):
        return f"<Assignment(id={self.id})>"

    @property
    def properties(self):
        data = self.data
        properties = list()
        if isinstance(data['appl_num'], list):
            for i in range(len(data["appl_num"])):
                properties.append(
                    {
                        "appl_id": data["appl_num"][i],
                        "app_filing_date": data["filing_date"][i],
                        "patent_number": data["pat_num"][i],
                        "pct_number": data["pct_num"][i],
                        "intl_publ_date": datetime.datetime.strptime(
                            data["intl_publ_date"][i], "%Y-%m-%d"
                        ).date()
                        if data["intl_publ_date"][i]
                        else None,
                        "intl_reg_num": data["intl_reg_num"][i],
                        "app_early_pub_date": datetime.datetime.strptime(
                            data["publ_date"][i], "%Y-%m-%d"
                        ).date()
                        if data["publ_date"][i]
                        else None,
                        "app_early_pub_number": data["publ_num"][i],
                        "patent_issue_date": data["issue_date"][i],
                        "patent_title": data["invention_title"][i],
                        "patent_title_lang": data["invention_title_lang"][i],
                        "inventors": data["inventors"][i],
                    }
                )
        else:
            properties.append(
                {
                    "appl_id": data["appl_num"],
                    "app_filing_date": data["filing_date"],
                    "patent_number": data["pat_num"],
                    "pct_number": data["pct_num"],
                    "intl_publ_date": data["intl_publ_date"] if data["intl_publ_date"] else None,
                    "intl_reg_num": data["intl_reg_num"],
                    "app_early_pub_date": data["publ_date"] if data["publ_date"] else None,
                    "app_early_pub_number": data["publ_num"],
                    "patent_issue_date": data["issue_date"],
                    "patent_title": data["invention_title"],
                    "patent_title_lang": data["invention_title_lang"],
                    "inventors": data["inventors"],
                }
            )

        return [Property(p) for p in properties]

    @property
    def correspondent(self):
        data = self.data
        correspondent_keys = filter(
            lambda x: "corr_" in x and "size" not in x, data.keys()
        )
        return repartition({k: data[k] for k in correspondent_keys})[0]

    @property
    def assignees(self):
        data = self.data
        assignee_keys = filter(
            lambda x: "pat_assignee_" in x and "size" not in x, data.keys()
        )
        return repartition({k: data[k] for k in assignee_keys})

    @property
    def assignors(self):
        data = self.data
        assignor_keys = filter(
            lambda x: "pat_assignor_" in x and "size" not in x, data.keys()
        )
        return repartition({k: data[k] for k in assignor_keys})

    def download(self):
        response = session.get(self.image_url, stream=True)
        with open(f"{self.id}.pdf", "wb") as f:
            f.write(response.raw.read())


class Property(Model):
    attrs = [
        "appl_id",
        "app_filing_date",
        "pct_number",
        "intl_publ_date",
        "app_early_pub_number",
        "app_early_pub_date",
        "patent_number",
        "patent_title",
        "inventors",
        "patent_issue_date",
    ]
    primary_key = "appl_id"
    us_application = one_to_one("patent_client.USApplication", appl_id="appl_id")


def repartition(dictionary):
    types = [type(v) for v in dictionary.values()]
    keys = list(dictionary.keys())
    print(dictionary)
    for i in range(min(len(k) for k in keys)):
        if not all(keys[0][i] == k[i] for k in keys):
            break

    if all(t == list() for t in types):
        lens = [len(v) for v in dictionary.values()]
        if not all(l == lens[0] for l in lens):
            raise ValueError("Not all keys have the same length!")

        output = list()
        for i in range(len(dictionary[keys[0]])):
            item = dict()
            for k in keys:
                new_key = k[i:]
                item[new_key] = dictionary[k][i]
            output.append(item)
        return output

    else:
        return [{k[i:]: dictionary[k] for k in keys}]
