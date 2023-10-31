from typing import Generic
from typing import TypeVar

from patent_client.util.base.manager import Manager

from . import public_search_async_api
from .model import Patent
from .model import PatentBiblio
from .model import PublicSearch
from .model import PublicSearchDocument
from .model import PublishedApplication
from .model import PublishedApplicationBiblio
from .query import QueryBuilder
from .schema import PublicSearchDocumentSchema
from .schema import PublicSearchSchema


class CapacityException(Exception):
    pass


class FinishedException(Exception):
    pass


T = TypeVar("T")


class GenericPublicSearchManager(Manager, Generic[T]):
    __schema__ = PublicSearchSchema
    page_size = 500
    primary_key = "patent_number"
    query_builder = QueryBuilder()

    async def _aget_results(self):
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        page_no = 0
        obj_counter = 0
        try:
            while True:
                page = await public_search_async_api.run_query(
                    query=query,
                    start=page_no * self.page_size,
                    limit=self.page_size,
                    sort=order_by,
                    sources=sources,
                )
                for obj in page["patents"]:
                    if self.config.limit and obj_counter >= self.config.limit + self.config.offset:
                        raise FinishedException()
                    if obj_counter >= self.config.offset:
                        yield self.__schema__.load(obj)
                    obj_counter += 1
                page_no += 1
                if len(page["patents"]) < self.page_size:
                    raise FinishedException()
        except FinishedException:
            pass

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
        if hasattr(self, "_len"):
            return self._len
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        page = await public_search_async_api.run_query(
            query=query, start=0, limit=self.page_size, sort=order_by, sources=sources
        )

        total_results = page["totalResults"]
        total_results -= self.config.offset
        if self.config.limit:
            self._len = min(self.config.limit, total_results)
        else:
            self._len = total_results
        return self._len


class GenericPublicSearchDocumentManager(GenericPublicSearchManager, Generic[T]):
    __doc_schema__ = PublicSearchDocumentSchema()

    async def _aget_results(self):
        result_count = super().__len__()
        if result_count > 20:
            raise CapacityException(
                f"Query would result in more than 20 results! ({result_count} > 20).\nPlease use the associated Biblio method to reduce load on the API (PublicSearch / PatentBiblio / PublishedApplicationBiblio"
            )

        async for obj in super()._aget_results():
            doc = await public_search_async_api.get_document(obj)
            yield self.__doc_schema__.load(doc)


class PublicSearchManager(GenericPublicSearchManager[PublicSearch]):
    pass


class PublicSearchDocumentManager(GenericPublicSearchDocumentManager[PublicSearchDocument]):
    pass


class PatentBiblioManager(GenericPublicSearchManager[PatentBiblio]):
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


class PublishedApplicationBiblioManager(GenericPublicSearchManager[PublishedApplicationBiblio]):
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
