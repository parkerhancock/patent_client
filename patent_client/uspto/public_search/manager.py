from typing import AsyncIterator
from typing import Generic
from typing import TypeVar

from .api import PublicSearchApi
from .model import Patent
from .model import PatentBiblio
from .model import PublicSearchBiblio
from .model import PublicSearchDocument
from .model import PublishedApplication
from .model import PublishedApplicationBiblio
from .query import QueryBuilder
from patent_client.util.manager import Manager
from patent_client.util.request_util import get_start_and_row_count


class CapacityException(Exception):
    pass


class FinishedException(Exception):
    pass


T = TypeVar("T")

public_search_api = PublicSearchApi()


class GenericPublicSearchManager(Manager, Generic[T]):
    page_size = 500
    default_filter = "patent_number"
    query_builder = QueryBuilder()

    @property
    def _query(self):
        return self.query_builder.build_query(self.config)

    @property
    def _order_by(self):
        return self.query_builder.build_order_by(self.config)

    @property
    def query_fields(self):
        return self.query_builder.search_keywords

    @property
    def order_by_fields(self):
        return self.query_builder.order_by_keywords

    async def alen(self):
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        page = await public_search_api.run_query(
            query=query, start=0, limit=self.page_size, sort=order_by, sources=sources
        )
        max_len = page.num_found - self.config.offset
        return min(self.config.limit, max_len) if self.config.limit else max_len


class GenericPublicSearchBiblioManager(GenericPublicSearchManager, Generic[T]):
    async def _aget_results(self) -> AsyncIterator[T]:
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        for start, rows in get_start_and_row_count(self.config.limit, self.config.offset, self.page_size):
            page = await public_search_api.run_query(
                query=query,
                start=start,
                limit=rows,
                sort=order_by,
                sources=sources,
            )
            for obj in page.docs:
                yield obj
            if len(page.docs) < rows:
                break


class GenericPublicSearchDocumentManager(GenericPublicSearchBiblioManager, Generic[T]):
    async def _aget_results(self) -> AsyncIterator["PublicSearchDocument"]:
        result_count = super().__len__()
        if result_count > 20:
            raise CapacityException(
                f"Query would result in more than 20 results! ({result_count} > 20).\nPlease use the associated Biblio method to reduce load on the API (PublicSearch / PatentBiblio / PublishedApplicationBiblio"
            )
        async for obj in super()._aget_results():
            doc = await public_search_api.get_document(obj)
            yield doc


class PublicSearchBiblioManager(GenericPublicSearchBiblioManager[PublicSearchBiblio]):
    pass


class PublicSearchDocumentManager(GenericPublicSearchDocumentManager[PublicSearchDocument]):
    pass


class PatentBiblioManager(GenericPublicSearchBiblioManager[PatentBiblio]):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "USPAT",
        ]


class PatentManager(GenericPublicSearchDocumentManager[Patent]):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "USPAT",
        ]


class PublishedApplicationBiblioManager(GenericPublicSearchBiblioManager[PublishedApplicationBiblio]):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "US-PGPUB",
        ]


class PublishedApplicationManager(GenericPublicSearchDocumentManager[PublishedApplication]):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "US-PGPUB",
        ]
