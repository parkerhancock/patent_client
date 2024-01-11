import typing as tp

from .model import Patent
from .model import PatentBiblio
from .model import PublicSearchBiblio
from .model import PublicSearchBiblioPage
from .model import PublicSearchDocument
from .model import PublishedApplication
from .model import PublishedApplicationBiblio
from .query import QueryBuilder
from patent_client._async.uspto.public_search import PublicSearchApi as PublicSearchAsyncApi
from patent_client._sync.uspto.public_search import PublicSearchApi as PublicSearchSyncApi
from patent_client.util.manager import Manager
from patent_client.util.request_util import get_start_and_row_count


class CapacityException(Exception):
    pass


class FinishedException(Exception):
    pass


T = tp.TypeVar("T")


class GenericPublicSearchManager(Manager, tp.Generic[T]):
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

    def len(self):
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        data = PublicSearchSyncApi.query(query=query, start=0, limit=self.page_size, sort=order_by, sources=sources)
        page = PublicSearchBiblioPage.model_validate(data)
        max_len = page.num_found - self.config.offset
        return min(self.config.limit, max_len) if self.config.limit else max_len

    async def alen(self):
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        data = await PublicSearchAsyncApi.query(
            query=query, start=0, limit=self.page_size, sort=order_by, sources=sources
        )
        page = PublicSearchBiblioPage.model_validate(data)
        max_len = page.num_found - self.config.offset
        return min(self.config.limit, max_len) if self.config.limit else max_len


class GenericPublicSearchBiblioManager(GenericPublicSearchManager, tp.Generic[T]):
    def _get_results(self) -> tp.Iterator[T]:
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        record_counter = 0
        for start, rows in get_start_and_row_count(self.config.limit, self.config.offset, self.page_size):
            data = PublicSearchSyncApi.query(
                query=query,
                start=start,
                limit=rows,
                sort=order_by,
                sources=sources,
            )
            page = PublicSearchBiblioPage.model_validate(data)
            for obj in page.docs:
                yield obj
                record_counter += 1
                if self.config.limit is not None and record_counter >= self.config.limit:
                    break
            if len(page.docs) < rows or (self.config.limit is not None and record_counter >= self.config.limit):
                break

    async def _aget_results(self) -> tp.AsyncIterator[T]:
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        for start, rows in get_start_and_row_count(self.config.limit, self.config.offset, self.page_size):
            data = await PublicSearchAsyncApi.query(
                query=query,
                start=start,
                limit=rows,
                sort=order_by,
                sources=sources,
            )
            page = PublicSearchBiblioPage.model_validate(data)
            for obj in page.docs:
                yield obj
            if len(page.docs) < rows:
                break


capacity_limit = 501


class GenericPublicSearchDocumentManager(GenericPublicSearchBiblioManager, tp.Generic[T]):
    def _get_results(self) -> tp.AsyncIterator["PublicSearchDocument"]:
        result_count = super().__len__()
        if result_count > capacity_limit:
            raise CapacityException(
                f"Query would result in more than 20 results! ({result_count} > 20).\nPlease use the associated Biblio method to reduce load on the API (PublicSearch / PatentBiblio / PublishedApplicationBiblio"
            )
        for obj in super()._get_results():
            data = PublicSearchSyncApi.get_document(obj.guid, obj.type)
            doc = PublicSearchDocument.model_validate(data)
            yield doc

    async def _aget_results(self) -> tp.AsyncIterator["PublicSearchDocument"]:
        result_count = super().__len__()
        if result_count > capacity_limit:
            raise CapacityException(
                f"Query would result in more than 20 results! ({result_count} > 20).\nPlease use the associated Biblio method to reduce load on the API (PublicSearch / PatentBiblio / PublishedApplicationBiblio"
            )
        async for obj in super()._aget_results():
            data = await PublicSearchAsyncApi.get_document(obj.guid, obj.type)
            doc = PublicSearchDocument.model_validate(data)
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
