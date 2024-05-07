import typing as tp

from patent_client.util.manager import AsyncManager
from patent_client.util.request_util import get_start_and_row_count

from .api import ODPApi
from .model import SearchRequest, USApplication, USApplicationBiblio
from .query import create_post_search_obj

if tp.TYPE_CHECKING:
    from .model import (
        Assignment,
        Continuity,
        CustomerNumber,
        Document,
        ForeignPriority,
        SearchResult,
        TermAdjustment,
        Transaction,
        USApplication,
        USApplicationBiblio,
    )


api = ODPApi()


class USApplicationManager(AsyncManager):
    default_filter = "appl_id"
    default_fields = ["applicationNumberText"]
    response_model = USApplication

    async def count(self):
        return (await api.post_search(self._create_search_obj(fields=["applicationNumberText"])))[
            "count"
        ]

    async def _get_results(self) -> tp.AsyncIterator["SearchResult"]:
        query_obj = self._create_search_obj()
        for start, rows in get_start_and_row_count(self.config.limit):
            page_query = query_obj.model_dump()
            page_query["pagination"] = {"offset": start, "limit": rows}
            page_query_obj = SearchRequest(**page_query)
            for result in (await api.post_search(page_query_obj))["patentBag"]:
                app_id = result["applicationNumberText"]
                app = await api.get_application_data(app_id)
                yield app

    def _create_search_obj(self, fields: tp.Optional[tp.List[str]] = None):
        if fields is None:
            fields = self.default_fields
        if "query" in self.config.filter:
            return SearchRequest(**self.config.filter["query"][0], fields=fields)
        elif "q" in self.config.filter:
            return SearchRequest(q=self.config.filter["q"][0], fields=fields)
        else:
            return create_post_search_obj(self.config, fields=fields)

    async def get(self, *args, **kwargs):
        if len(args) == 1 and not kwargs:
            return await api.get_application_data(args[0])
        return await super().get(*args, **kwargs)


class USApplicationBiblioManager(USApplicationManager):
    default_filter = "appl_id"
    default_fields = [
        "firstInventorToFileIndicator",
        "filingDate",
        "inventorBag",
        "customerNumber",
        "groupArtUnitNumber",
        "inventionTitle",
        "correspondenceAddressBag",
        "applicationConfirmationNumber",
        "docketNumber",
        "applicationNumberText",
        "firstInventorName",
        "firstApplicantName",
        "cpcClassificationBag",
        "businessEntityStatusCategory",
        "earliestPublicationNumber",
    ]
    response_model = USApplicationBiblio

    async def _get_results(self) -> tp.AsyncIterator["SearchResult"]:
        query_obj = self._create_search_obj(fields=self.default_fields)
        for start, rows in get_start_and_row_count(self.config.limit):
            page_query = query_obj.model_dump()
            page_query["pagination"] = {"offset": start, "limit": rows}
            page_query_obj = SearchRequest(**page_query)
            for result in (await api.post_search(page_query_obj))["patentBag"]:
                yield self.response_model(**result)

    async def get(self, *args, **kwargs):
        if len(args) == 1 and not kwargs:
            return await api.get_application_biblio_data(args[0])
        return await super().get(*args, **kwargs)


class AttributeManager(AsyncManager):
    def filter(self, *args, **kwargs):
        raise NotImplementedError("Filtering attributes is not supported")

    def get(self, *args, **kwargs):
        raise NotImplementedError("Getting attributes is not supported")

    def limit(self, *args, **kwargs):
        raise NotImplementedError("Limit is not supported")

    def offset(self, *args, **kwargs):
        raise NotImplementedError("Offset is not supported")


class ContinuityManager(AttributeManager):
    def get(self, appl_id: str) -> "Continuity":
        return api.get_continuity_data(appl_id)


class DocumentManager(AsyncManager):
    default_filter = "appl_id"

    async def count(self):
        return len(await api.get_documents(self.config.filter["appl_id"][0]))

    async def _get_results(self) -> tp.AsyncIterator["Document"]:
        for doc in await api.get_documents(self.config.filter["appl_id"][0]):
            yield doc


class TermAdjustmentManager(AsyncManager):
    default_filter = "appl_id"

    async def _get_results(self) -> "TermAdjustment":
        return await api.get_term_adjustments(self.config.filter["appl_id"][0])


class AssignmentManager(AsyncManager):
    default_filter = "appl_id"

    async def _get_results(self) -> tp.AsyncIterator["Assignment"]:
        for doc in await api.get_assignments(self.config.filter["appl_id"][0]):
            yield doc

    async def count(self):
        return len(await api.get_assignments(self.config.filter["appl_id"][0]))


class CustomerNumberManager(AsyncManager):
    default_filter = "appl_id"

    async def _get_results(self) -> "CustomerNumber":
        return await api.get_customer_numbers(self.config.filter["appl_id"][0])


class ForeignPriorityManager(AsyncManager):
    default_filter = "appl_id"

    async def _get_results(self) -> "ForeignPriority":
        for doc in await api.get_foreign_priority_data(self.config.filter["appl_id"][0]):
            yield doc


class TransactionManager(AsyncManager):
    default_filter = "appl_id"

    async def _get_results(self) -> tp.AsyncIterator["Transaction"]:
        for doc in await api.get_transactions(self.config.filter["appl_id"][0]):
            yield doc

    async def count(self):
        return len(await api.get_transactions(self.config.filter["appl_id"][0]))
