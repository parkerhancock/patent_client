from collections.abc import Sequence

from dateutil.parser import parse as parse_dt
from patent_client.util.base.manager import Manager

from .api import PublicSearchApi
from .keywords import keywords
from .schema import PublicSearchDocumentSchema
from .schema import PublicSearchSchema


class QueryException(Exception):
    pass


class PublicSearchManager(Manager):
    __schema__ = PublicSearchSchema
    page_size = 500
    primary_key = "patent_number"

    def _get_results(self):
        query = self._get_query()
        order_by = self._get_order_by()
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        page_no = 0
        obj_counter = 0
        while True:
            page = PublicSearchApi.run_query(
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

    def __len__(self):
        if hasattr(self, "_len"):
            return self._len
        query = self._get_query()
        order_by = self._get_order_by()
        sources = self.config.options.get("sources", ["US-PGPUB", "USPAT", "USOCR"])
        page = PublicSearchApi.run_query(query=query, start=0, limit=self.page_size, sort=order_by, sources=sources)

        total_results = page["totalResults"]
        total_results -= self.config.offset
        if self.config.limit:
            self._len = min(self.config.limit, total_results)
        else:
            self._len = total_results
        return self._len

    def _get_order_by(self):
        if not self.config.order_by:
            return "date_publ desc"
        order_str = list()
        for value in self.config.order_by:
            if value.startswith("+"):
                order_str.append(f"{value[1:]} asc")
            elif value.startswith("-"):
                order_str.append(f"{value[1:]} desc")
            else:
                order_str.append(f"{value} asc")
        return " ".join(order_str)

    def _query_value(self, key, value):
        if isinstance(value, str) and "->" in value:
            start, end = value.split("->")
            return f"@{keywords[key]}>={parse_dt(start).strftime('%Y%m%d')}<={parse_dt(end).strftime('%Y%m%d')}"
        else:
            return f'("{value}")[{keywords[key]}]'

    def _get_query(self):
        if "query" in self.config.filter:
            return self.config.filter["query"]
        query_components = list()
        for key, value in self.config.filter.items():
            if key not in keywords:
                raise QueryException(f"{key} is not a valid search field!")
            if isinstance(value, Sequence) and not isinstance(value, str):
                query_components += [self._query_value(key, v) for v in value]
            else:
                query_components.append(self._query_value(key, value))
        default_operator = self.config.options.get("default_operator", "AND")
        return f" {default_operator} ".join(query_components)


class PublicSearchDocumentManager(PublicSearchManager):
    __doc_schema__ = PublicSearchDocumentSchema()

    def _get_results(self):
        for obj in super()._get_results():
            doc = PublicSearchApi.get_document(obj)
            yield self.__doc_schema__.load(doc)


class PatentBiblioManager(PublicSearchManager):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "USPAT",
        ]


class PatentManager(PublicSearchDocumentManager, PatentBiblioManager):
    pass


class PublishedApplicationBiblioManager(PublicSearchManager):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config.options["sources"] = [
            "US-PGPUB",
        ]


class PublishedApplicationManager(PublicSearchDocumentManager, PublishedApplicationBiblioManager):
    pass
