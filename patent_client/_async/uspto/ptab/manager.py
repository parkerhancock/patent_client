from typing import AsyncIterator

import inflection

from patent_client._async.uspto.ptab.api import ptab_client
from patent_client._async.uspto.ptab.model import PtabDecision, PtabDocument, PtabProceeding
from patent_client._async.uspto.ptab.schema import SearchInput
from patent_client.util.manager import AsyncManager
from patent_client.util.request_util import get_start_and_row_count

from .errors import InvalidFieldError
from .schema_parser import ALLOWED_FIELDS


class PtabBaseManager(AsyncManager):
    default_page_size = 25

    def __init__(self, config=None):
        super().__init__(config)

    async def _get_results(self) -> AsyncIterator[PtabProceeding]:
        search_input = self._build_search_input()
        limit = self.config.limit
        offset = self.config.offset
        for start, row_count in get_start_and_row_count(limit, offset, self.default_page_size):
            if isinstance(search_input, SearchInput):
                search_input.record_start_number = start
                search_input.record_total_quantity = row_count
            else:
                # If it's a raw query, we need to create a new SearchInput object
                search_input = SearchInput(
                    search_text=search_input,
                    record_start_number=start,
                    record_total_quantity=row_count,
                )
            response = await self._search(search_input)

            for result in response.results:
                yield self.model(**result)

            if len(response.results) < row_count:
                # We've reached the end of the results
                break

    def _build_search_input(self) -> SearchInput:
        if "raw_query" in self.config.filter:
            return SearchInput.model_validate(self.config.filter["raw_query"])

        search_text = self._build_search_text()
        return SearchInput(
            search_text=search_text,
            sort_data_bag=[
                {"sortField": field, "sortOrder": order.value}
                for field, order in self.config.order_by
            ],
        )

    def _get_allowed_fields(self) -> set:
        return ALLOWED_FIELDS[self.endpoint]

    def _build_search_text(self) -> str:
        if "query" in self.config.filter:
            return self.config.filter["query"]

        allowed_fields = self._get_allowed_fields()
        query_parts = []
        for field, value in self.config.filter.items():
            field_name = inflection.camelize(field, uppercase_first_letter=False)
            if field_name not in allowed_fields:
                raise InvalidFieldError(
                    f"Invalid field: {field}. Allowed fields are: {', '.join(allowed_fields)}"
                )

            if isinstance(value, (list, tuple)):
                or_values = " OR ".join(f'"{v}"' for v in value)
                query_parts.append(f"{field_name}:({or_values})")
            else:
                query_parts.append(f'{field_name}:"{value}"')
        return " AND ".join(query_parts)

    async def count(self) -> int:
        search_input = self._build_search_input()
        if isinstance(search_input, SearchInput):
            search_input.record_start_number = 0
            search_input.record_total_quantity = 1
        else:
            # If it's a raw query, we need to create a new SearchInput object
            search_input = SearchInput(
                search_text=search_input,
                record_start_number=0,
                record_total_quantity=1,
            )

        response = await self._search(search_input)
        total_count = response.record_total_quantity

        if self.config.limit is not None:
            return min(total_count, self.config.limit)
        return total_count

    async def _search(self, search_input: SearchInput):
        raise NotImplementedError("Subclasses must implement this method")


class PtabProceedingManager(PtabBaseManager):
    model = PtabProceeding
    default_filter = "proceeding_number"
    endpoint = "proceedings"

    async def _search(self, search_input: SearchInput):
        return await ptab_client.proceedings.search(search_input)


class PtabDocumentManager(PtabBaseManager):
    model = PtabDocument
    default_filter = "proceeding_number"
    endpoint = "documents"

    async def _search(self, search_input: SearchInput):
        return await ptab_client.documents.search(search_input)

    async def download(self, document_identifier: str) -> bytes:
        return await ptab_client.documents.download(document_identifier)

    async def download_trial_documents(self, proceeding_number: str) -> bytes:
        return await ptab_client.documents.download_trial_documents(proceeding_number)


class PtabDecisionManager(PtabBaseManager):
    model = PtabDecision
    default_filter = "proceeding_number"
    endpoint = "decisions"

    async def _search(self, search_input: SearchInput):
        return await ptab_client.decisions.search(search_input)
