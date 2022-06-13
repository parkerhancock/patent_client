import math
import re
import typing
import warnings
from collections.abc import Iterable

from urllib3.connectionpool import InsecureRequestWarning

from patent_client import session
from patent_client.util import Manager

from .model import Assignment
from .parser import AssignmentParser
from .schema import AssignmentSchema

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

NUMBER_CLEAN_RE = re.compile(r"[^\d]")
clean_number = lambda x: NUMBER_CLEAN_RE.sub("", str(x))


class AssignmentManager(Manager[Assignment]):
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
    url = "https://assignment-api.uspto.gov/patent/lookup"
    page_size = 20
    obj_class = "patent_client.uspto_assignments.Assignment"
    primary_key = "id"

    def __init__(self, *args, **kwargs):
        super(AssignmentManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    @property
    def allowed_filters(self):
        return list(self.fields.keys())

    def _get_results(self) -> typing.Iterator[Assignment]:
        num_pages = math.ceil(len(self) / self.page_size)
        page_num = 0
        counter = 0
        for page_num in range(num_pages):
            for item in self.get_page(page_num):
                if not self.config["limit"] or counter < self.config["limit"]:
                    yield AssignmentSchema().load(item)
                counter += 1
            page_num += 1

    def get_query(self, page_no):
        """Get assignments.
        Args:
            patent: pat no to search
            application: app no to search
            assignee: assignee name to search
        """

        for key, value in self.config["filter"].items():
            field = self.fields[key]
            query = value
        if field in ["PatentNumber", "ApplicationNumber"]:
            if isinstance(query, Iterable) and not isinstance(query, str):
                query = [clean_number(q) for q in query]
            else:
                query = clean_number(query)

        sort = list()
        for p in self.config["order_by"]:
            if sort[0] == "-":
                sort.append(p[1:] + "+desc")
            else:
                sort.append(p + "+asc")

        return {
            "filter": field,
            "query": " OR ".join(query) if isinstance(query, list) else query,
            "rows": self.page_size,
            "start": page_no * self.page_size,
            "sort": " ".join(sort),
        }

    def __len__(self) -> int:
        if not hasattr(self, "_len"):
            self.get_page(0)
        max_length = self._len - self.config["offset"]
        limit = self.config["limit"]
        if not limit:
            return max_length
        else:
            return limit if limit < max_length else max_length

    def get_page(self, page_no):
        params = self.get_query(page_no)
        response = session.get(
            self.url,
            params=params,
            verify=False,
            headers={"Accept": "application/xml"},
        )
        text = response.text
        self._len, page = self.parser.parse(text)
        return page

    @property
    def query_fields(self):
        fields = self.fields
        for k in sorted(fields.keys()):
            print(k)
