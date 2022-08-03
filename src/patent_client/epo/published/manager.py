from warnings import warn

from patent_client.util import Manager

from .api import PublishedApi
from .cql import generate_query


class SearchManager(Manager):
    result_size = 100
    primary_key = "publication"

    def _get_search_results_range(self, start=1, end=100):
        if "cql_query" in self.config["filter"]:
            query = self.config["filter"]["cql_query"]
        else:
            query = generate_query(**self.config["filter"])
        return PublishedApi.search.search(query, start, end)

    def __len__(self):
        page = self._get_search_results_range(1, 2)
        offset = self.config["offset"] or 0
        limit = self.config["limit"] or page.num_results - offset
        num_results = page.num_results
        num_results -= offset
        num_results = min(limit, num_results)
        return num_results

    def _get_results(self):
        num_pages = round(len(self) / self.result_size)
        limit = self.config["limit"] or len(self)
        offset = self.config["offset"] or 0
        max_position = offset + limit

        range = (offset + 1, min(offset + self.result_size, max_position))
        while True:
            page = self._get_search_results_range(*range)
            for result in page.results:
                yield result
            if range[1] == max_position:
                break
            range = (range[0] + self.result_size, min(range[1] + self.result_size, max_position))

    def get(self, number, doc_type="publication", format="docdb"):
        result = PublishedApi.biblio.get_biblio(number, doc_type, format)
        if len(result.documents) > 1:
            raise Exception("More than one result found! Try another query")
        return result.documents[0]


class BiblioManager(Manager):
    def get(self, doc_number):
        result = PublishedApi.biblio.get_biblio(doc_number)
        if len(result.documents) > 1:
            raise ValueError(f"More than one result found for {doc_number}!")
        return result.documents[0]


class ClaimsManager(Manager):
    def get(self, doc_number):
        return PublishedApi.fulltext.get_claims(doc_number)


class DescriptionManager(Manager):
    def get(self, doc_number):
        return PublishedApi.fulltext.get_description(doc_number)


class ImageManager(Manager):
    def get(self, doc_number):
        return PublishedApi.images.get_images(doc_number)
