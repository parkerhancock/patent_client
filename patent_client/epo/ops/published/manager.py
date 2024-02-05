import math

from .cql import generate_query
from .model.biblio import BiblioResult
from .model.fulltext import Claims
from .model.fulltext import Description
from .model.images import ImageDocument
from .model.images import Images
from .model.search import Search
from patent_client._async.epo.published import PublishedApi as PublishedAsyncApi
from patent_client._sync.epo.published import PublishedApi as PublishedSyncApi
from patent_client.util.manager import Manager


def get_ranges(limit=None, offset=0, page_size=100):
    offset = offset or 0
    offset += 1
    if not limit:
        page_no = 0
        while True:
            start = page_no * page_size + offset
            yield (start, start + page_size - 1)
            page_no += 1
    else:
        num_full_pages = math.floor(limit / page_size)
        last_page_size = limit % page_size
        for i in range(num_full_pages):
            start = i * page_size + offset
            yield (start, start + page_size - 1)
        if last_page_size:
            start = num_full_pages * page_size + offset
            yield (start, start + last_page_size - 1)


class SearchManager(Manager["BiblioResult"]):
    result_size = 100
    primary_key = "publication"

    def _get_search_results_range(self, start=1, end=100):
        if "cql_query" in self.config.filter:
            query = self.config.filter["cql_query"]
        else:
            query = generate_query(**self.config.filter)
        data = PublishedSyncApi.search.search(query, start, end)
        return Search.model_validate(data)

    def _get_results(self):
        for start, end in get_ranges(self.config.limit, self.config.offset, self.result_size):
            page = self._get_search_results_range(start, end)
            for result in page.results:
                yield result
            if len(page.results) < self.result_size:
                break

    def get(self, number, doc_type="publication", format="docdb") -> BiblioResult:
        data = PublishedSyncApi.biblio.get_biblio(number, doc_type, format)
        result = BiblioResult.model_validate(data)
        if len(result.documents) > 1:
            raise Exception("More than one result found! Try another query")
        return result.documents[0]

    def len(self) -> int:
        page = self._get_search_results_range(1, 100)
        offset = self.config.offset or 0
        limit = self.config.limit or page.num_results - offset
        num_results = page.num_results
        num_results -= offset
        num_results = min(limit, num_results)
        return num_results

    async def _aget_search_results_range(self, start=1, end=100):
        if "cql_query" in self.config.filter:
            query = self.config.filter["cql_query"]
        else:
            query = generate_query(**self.config.filter)
        data = await PublishedAsyncApi.search.search(query, start, end)
        return Search.model_validate(data)

    async def _aget_results(self):
        for start, end in get_ranges(self.config.limit, self.config.offset, self.result_size):
            page = await self._aget_search_results_range(start, end)
            for result in page.results:
                yield result
            if len(page.results) < self.result_size:
                break

    async def aget(self, number, doc_type="publication", format="docdb") -> BiblioResult:
        data = await PublishedAsyncApi.biblio.get_biblio(number, doc_type, format)
        result = BiblioResult.model_validate(data)
        if len(result.documents) > 1:
            raise Exception("More than one result found! Try another query")
        return result.documents[0]

    async def alen(self) -> int:
        page = await self._aget_search_results_range(1, 100)
        offset = self.config.offset or 0
        limit = self.config.limit or page.num_results - offset
        num_results = page.num_results
        num_results -= offset
        num_results = min(limit, num_results)
        return num_results


class BiblioManager(Manager):
    def get(self, doc_number) -> "BiblioResult":
        data = PublishedSyncApi.biblio.get_biblio(doc_number)
        result = BiblioResult.model_validate(data)
        if len(result.documents) > 1:
            raise ValueError(f"More than one result found for {doc_number}!")
        return result.documents[0]

    async def aget(self, doc_number) -> "BiblioResult":
        data = await PublishedAsyncApi.biblio.get_biblio(doc_number)
        result = BiblioResult.model_validate(data)
        if len(result.documents) > 1:
            raise ValueError(f"More than one result found for {doc_number}!")
        return result.documents[0]


class ClaimsManager(Manager):
    def get(self, doc_number) -> "Claims":
        data = PublishedSyncApi.fulltext.get_claims(doc_number)
        return Claims.model_validate(data)

    async def aget(self, doc_number) -> "Claims":
        data = await PublishedAsyncApi.fulltext.get_claims(doc_number)
        return Claims.model_validate(data)


class DescriptionManager(Manager):
    def get(self, doc_number) -> Description:
        data = PublishedSyncApi.fulltext.get_description(doc_number)
        return Description.model_validate(data)

    async def aget(self, doc_number) -> Description:
        data = await PublishedAsyncApi.fulltext.get_description(doc_number)
        return Description.model_validate(data)


class ImagesManager(Manager):
    def get(self, doc_number) -> ImageDocument:
        data = PublishedSyncApi.images.get_images(doc_number)
        return Images.model_validate(data)

    async def aget(self, doc_number) -> ImageDocument:
        data = await PublishedAsyncApi.images.get_images(doc_number)
        return Images.model_validate(data)


class InpadocManager(SearchManager):
    pass


class InpadocBiblioManager(BiblioManager):
    pass
