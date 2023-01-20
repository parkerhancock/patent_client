import logging
import math
import re
import typing
import warnings
from collections.abc import Sequence

from patent_client import session
from patent_client.util import Manager
from urllib3.connectionpool import InsecureRequestWarning

from .model import Assignment
from .schema import AssignmentPageSchema

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

NUMBER_CLEAN_RE = re.compile(r"[^\d]")
clean_number = lambda x: NUMBER_CLEAN_RE.sub("", str(x))


logger = logging.getLogger(__name__)


class AssignmentManager(Manager[Assignment]):
    __schema__ = AssignmentPageSchema()
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
                if not self.config.limit or counter < self.config.limit:
                    yield item
                counter += 1
            page_num += 1

    def get_query(self, page_no):
        """Get assignments.
        Args:
            patent: pat no to search
            application: app no to search
            assignee: assignee name to search
        """

        for key, value in self.config.filter.items():
            field = self.fields[key]
            query = value
        if field in ["PatentNumber", "ApplicationNumber"]:
            if isinstance(query, Sequence) and not isinstance(query, str):
                query = [clean_number(q) for q in query]
            else:
                query = clean_number(query)

        sort = list()
        for p in self.config.order_by:
            if sort[0] == "-":
                sort.append(p[1:] + "+desc")
            else:
                sort.append(p + "+asc")

        if isinstance(query, list):
            query = [f'"{q}"' for q in query]

        query = {
            "filter": field,
            "query": " OR ".join(query) if isinstance(query, Sequence) and not isinstance(query, str) else query,
            "rows": self.page_size,
            "start": page_no * self.page_size,
            "sort": " ".join(sort),
            "facet": False,
        }
        logger.info(f"Assignment Manager executed query {query}")
        return query

    def __len__(self) -> int:
        if not hasattr(self, "_len"):
            self.get_page(0)
        max_length = self._len - self.config.offset
        limit = self.config.limit
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
        result = self.__schema__.load(text)
        self._len = result.num_found
        return result.docs

    @property
    def query_fields(self):
        fields = self.fields
        for k in sorted(fields.keys()):
            print(k)
