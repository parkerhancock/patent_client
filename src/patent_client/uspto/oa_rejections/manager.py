import logging
from typing import AsyncIterator
from typing import Generic
from typing import TypeVar

import inflection
from patent_client.util.asyncio_util import run_sync
from patent_client.util.base.manager import Manager
from patent_client.util.request_util import get_start_and_row_count

from .api import OfficeActionApi
from .model import OfficeActionRejection


logger = logging.getLogger(__name__)


class HttpException(Exception):
    pass


T = TypeVar("T")


class OfficeActionManager(Manager, Generic[T]):
    primary_key = "id"
    page_size = 100
    fields_method = None
    records_method = None

    def __init__(self, *args, **kwargs):
        super(OfficeActionManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    def order_by(self):
        raise NotImplementedError("Office Action API does not support ordering")

    async def alen(self):
        max_length = (await self.records_method(self.get_query())).num_found
        return min(max_length, self.config.limit) if self.config.limit else max_length

    async def _aget_results(self) -> AsyncIterator[OfficeActionRejection]:
        query_params = self.get_query()
        for start, rows in get_start_and_row_count(self.config.limit, self.config.offset, self.page_size):
            page = await self.records_method(query_params, start=start, rows=rows)
            for item in page.docs:
                yield item
            if len(page.docs) < rows:
                break

    def get_query(self):
        if "query" in self.config.filter:
            query_text = self.config.filter["query"]
        else:
            query = list()
            for k, v in self.config.filter.items():
                if k == "appl_id":
                    field = "patentApplicationNumber"
                else:
                    field = inflection.camelize(k, uppercase_first_letter=False)
                if not v:
                    continue
                elif type(v) in (list, tuple):
                    v = (str(i) for i in v)
                    body = " OR ".join(f'"{value}"' if " " in value else value for value in v)
                else:
                    body = v
                query.append(f"{field}:({body})")
            query_text = " AND ".join(query).strip()
        return query_text

    def get_fields(self):
        return run_sync(self.aget_fields())

    async def aget_fields(self):
        return await self.fields_method()


class OfficeActionRejectionManager(OfficeActionManager[OfficeActionRejection]):
    fields_method = OfficeActionApi.get_rejection_fields
    records_method = OfficeActionApi.get_rejection_records


class OfficeActionCitationManager(OfficeActionManager[OfficeActionRejection]):
    fields_method = OfficeActionApi.get_citation_fields
    records_method = OfficeActionApi.get_citation_records


class OfficeActionFullTextManager(OfficeActionManager[OfficeActionRejection]):
    fields_method = OfficeActionApi.get_fulltext_fields
    records_method = OfficeActionApi.get_fulltext_records
