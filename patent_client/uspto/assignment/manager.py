import logging
import re
import typing as tp
import warnings
from collections.abc import Sequence

from urllib3.connectionpool import InsecureRequestWarning

from .convert import convert_xml_to_json
from .model import Assignment
from .model import AssignmentPage
from patent_client._async.uspto.assignment import AssignmentApi as AssignmentAsyncApi
from patent_client._sync.uspto.assignment import AssignmentApi as AssignmentSyncApi
from patent_client.util.manager import Manager
from patent_client.util.request_util import get_start_and_row_count

warnings.filterwarnings("ignore", category=InsecureRequestWarning)

NUMBER_CLEAN_RE = re.compile(r"[^\d]")
clean_number = lambda x: NUMBER_CLEAN_RE.sub("", str(x))


logger = logging.getLogger(__name__)


class AssignmentManager(Manager["Assignment"]):
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
    page_size = 100
    obj_class = "patent_client.uspto_assignments.Assignment"
    default_filter = "id"

    def __init__(self, *args, **kwargs):
        super(AssignmentManager, self).__init__(*args, **kwargs)

    @property
    def allowed_filters(self):
        return list(self.fields.keys())

    async def _aget_results(self) -> tp.AsyncIterator["Assignment"]:
        for start, rows in get_start_and_row_count(self.config.limit, self.config.offset, self.page_size):
            tree = await AssignmentAsyncApi.lookup(**{**self.get_query(), "start": start, "rows": rows})
            page = AssignmentPage.model_validate(convert_xml_to_json(tree))
            for doc in page.docs:
                yield doc
            if len(page.docs) < rows:
                break

    def _get_results(self) -> tp.Iterator["Assignment"]:
        for start, rows in get_start_and_row_count(self.config.limit, self.config.offset, self.page_size):
            tree = AssignmentSyncApi.lookup(**{**self.get_query(), "start": start, "rows": rows})
            page = AssignmentPage.model_validate(convert_xml_to_json(tree))
            for doc in page.docs:
                yield doc
            if len(page.docs) < rows:
                break

    def get_query(self):
        """Get assignments.
        Args:
            patent: pat no to search
            application: app no to search
            assignee: assignee name to search
        """
        if len(self.config.filter) > 1:
            raise ValueError("Assignment API does not support multiple filters!")
        for key, value in self.config.filter.items():
            if isinstance(value, Sequence) and not isinstance(value, str):
                if len(value) > 1:
                    raise ValueError("Assignment API does not support multiple values!")
                else:
                    value = value[0]
            field = self.fields[key]
            query = value
        if field in ["PatentNumber", "ApplicationNumber"]:
            query = clean_number(query)
        # Handle Ordering
        order_map = {"execution_date": "ExecutionDate+asc", "-execution_date": "ExecutionDate+desc"}
        if len(self.config.order_by) > 1:
            raise ValueError("Assignment API does not support multiple sort parameters!")
        elif len(self.config.order_by) == 1:
            sort = order_map[self.config.order_by[0]]
        else:
            sort = "ExecutionDate+desc"

        # if isinstance(query, list):
        #    query = [f'"{q}"' for q in query]

        query = {
            "filter": field,
            "query": query,
            "sort": sort,
        }
        return query

    async def alen(self) -> int:
        tree = await AssignmentAsyncApi.lookup(**self.get_query())
        page = AssignmentPage.model_validate(convert_xml_to_json(tree))
        max_len = page.num_found
        return min(max_len, self.config.limit) if self.config.limit else max_len

    def len(self) -> int:
        tree = AssignmentSyncApi.lookup(**self.get_query())
        page = AssignmentPage.model_validate(convert_xml_to_json(tree))
        max_len = page.num_found
        return min(max_len, self.config.limit) if self.config.limit else max_len

    @property
    def query_fields(self):
        fields = self.fields
        for k in sorted(fields.keys()):
            print(k)
