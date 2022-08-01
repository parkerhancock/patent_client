import math
import os

import xmltodict

from patent_client import CACHE_CONFIG
from patent_client import SETTINGS
from patent_client.util import Manager
from patent_client.util.manager import resolve

from ..ops.session import NS
from ..ops.session import session
from .schema import InpadocBiblioSchema
from .schema import InpadocResultSchema

SEARCH_FIELDS = {
    "title": "title",
    "abstract": "abstract",
    "title_and_abstract": "titleandabstract",
    "inventor": "inventor",
    "applicant": "applicant",
    "inventor_or_applicant": "inventorandapplicant",
    "publication": "publicationnumber",
    "epodoc_publication": "spn",
    "application": "applicationnumber",
    "epodoc_application": "sap",
    "priority": "prioritynumber",
    "epodoc_priority": "spr",
    "number": "num",  # Pub, App, or Priority Number
    "publication_date": "publicationdate",  # yyyy, yyyyMM, yyyyMMdd, yyyy-MM, yyyy-MM-dd
    "citation": "citation",
    "cited_in_examination": "ex",
    "cited_in_opposition": "op",
    "cited_by_applicant": "rf",
    "other_citation": "oc",
    "family": "famn",
    "cpc_class": "cpc",
    "ipc_class": "ipc",
    "ipc_core_invention_class": "ci",
    "ipc_core_additional_class": "cn",
    "ipc_advanced_class": "ai",
    "ipc_advanced_additional_class": "an",
    "ipc_core_class": "c",
    "classification": "cl",  # IPC or CPC Class
    "full_text": "txt",  # title, abstract, inventor and applicant
}


class OPSException(Exception):
    pass


class InpadocManager(Manager):
    page_size = 20
    primary_key = "publication"
    constituent = None

    def __init__(self, *args, **kwargs):
        super(InpadocManager, self).__init__(*args, **kwargs)
        self.pages = dict()

    def __len__(self):
        page = self.get_page(0)
        max_length = int(resolve(page, "@total-result-count"))
        limit = self.config["limit"]
        if limit:
            return limit if limit < max_length else max_length
        else:
            return max_length

    def _get_results(self):
        offset = self.config["offset"]
        limit = self.config["limit"]

        def result_gen(offset, limit):
            num_pages = math.ceil(len(self) / self.page_size)
            page_num = int(offset / self.page_size)
            counter = page_num * self.page_size
            while page_num < num_pages:
                page_data = self.get_page(page_num)
                data = resolve(page_data, self.item_path)
                if not isinstance(data, list):
                    yield counter, data
                    counter += 1
                else:
                    for item in data:
                        if not self.config["limit"] or counter < self.config["limit"]:
                            yield counter, item
                        counter += 1
                page_num += 1

        # Implement limit and offset
        for counter, item in result_gen(offset, limit):
            if limit is not None and counter - offset > limit:
                break
            if counter >= offset:
                yield self.schema.load(item)

    @property
    def search_url(self):
        if self.constituent:
            return f"http://ops.epo.org/3.2/rest-services/published-data/search/{self.constituent}"
        return "http://ops.epo.org/3.2/rest-services/published-data/search"

    @property
    def item_path(self):
        if self.constituent:
            return "search-result.exchange-documents"
        else:
            return "search-result.publication-reference"

    @property
    def schema(self):
        if self.constituent == "biblio":
            return InpadocBiblioSchema()
        elif self.constituent is None:
            return InpadocResultSchema()

    def get_page(self, page_number):
        if page_number not in self.pages:
            query_params = self.query_params(page_number)
            response = session.get(self.search_url, params=query_params, timeout=10)
            data = xmltodict.parse(
                response.text, process_namespaces=True, namespaces=NS
            )
            self.pages[page_number] = resolve(data, "world-patent-data.biblio-search")
        return self.pages[page_number]

    def query_params(self, page_number):
        query_dict = self.config["filter"]
        start = page_number * self.page_size + 1
        range_q = f"{start}-{start + self.page_size}"
        if "cql_query" in query_dict:
            return dict(q=query_dict["cql_query"], Range=range_q)
        query = ""
        for keyword, values in query_dict.items():
            for value in values:
                if keyword:
                    query += f'{SEARCH_FIELDS[keyword]}="{value}",'
        query = dict(q=query, Range=range_q)
        return query


class InpadocBiblioManager(InpadocManager):
    constituent = "biblio"
