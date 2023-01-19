from patent_client.util.base.manager import Manager

from . import public_search_api
from .query import QueryBuilder
from .schema import PublicSearchDocumentSchema
from .schema import PublicSearchSchema


class CapacityException(Exception):
    pass


class PublicSearchManager(Manager):
    __schema__ = PublicSearchSchema
    page_size = 500
    primary_key = "patent_number"
    query_builder = QueryBuilder()

    def _get_results(self):
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        page_no = 0
        obj_counter = 0
        while True:
            page = public_search_api.run_query(
                query=query, start=page_no * self.page_size, limit=self.page_size, sort=order_by, sources=sources
            )
            for obj in page["patents"]:
                if self.config.limit and obj_counter >= self.config.limit:
                    break
                yield self.__schema__.load(obj)
                obj_counter += 1
            page_no += 1
            if len(page["patents"]) < self.page_size:
                break

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

    def __len__(self):
        if hasattr(self, "_len"):
            return self._len
        query = self._query
        order_by = self._order_by
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        page = public_search_api.run_query(query=query, start=0, limit=self.page_size, sort=order_by, sources=sources)

        total_results = page["totalResults"]
        total_results -= self.config.offset
        if self.config.limit:
            self._len = min(self.config.limit, total_results)
        else:
            self._len = total_results
        return self._len


class PublicSearchDocumentManager(PublicSearchManager):
    __doc_schema__ = PublicSearchDocumentSchema()

    def _get_results(self):
        result_count = super().__len__()
        if result_count > 20:
            raise CapacityException(
                f"Query would result in more than 20 results! ({result_count} > 20).\nPlease use the associated Biblio method to reduce load on the API (PublicSearch / PatentBiblio / PublishedApplicationBiblio"
            )

        for obj in super()._get_results():
            doc = public_search_api.get_document(obj)
            yield self.__doc_schema__.load(doc)


class PatentBiblioManager(PublicSearchManager):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "USPAT",
        ]


class PatentManager(PublicSearchDocumentManager):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "USPAT",
        ]


class PublishedApplicationBiblioManager(PublicSearchManager):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "US-PGPUB",
        ]


class PublishedApplicationManager(PublicSearchDocumentManager):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "US-PGPUB",
        ]
