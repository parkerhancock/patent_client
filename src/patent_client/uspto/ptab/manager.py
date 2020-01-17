import math
from typing import Iterable, Generic
import inflection

from patent_client.util import Manager, ModelType
from patent_client import session

from .schema import PtabProceedingSchema, PtabDocumentSchema, PtabDecisionSchema
from .model import PtabProceeding, PtabDocument, PtabDecision
from .util import conversions, peds_to_ptab

class PtabManager(Manager, Generic[ModelType]):
    page_size = 25
    instance_schema = None

    def _get_results(self):
        total = self._len()
        offset = self.config["offset"]
        limit = self.config["limit"]
        if limit:
            max_item = total if total - offset < limit else offset + limit
        else:
            max_item = total
        item_range = (offset, max_item)
        page_range = (
            int(offset / self.page_size),
            math.ceil(max_item / self.page_size),
        )
        counter = page_range[0] * self.page_size

        for p in range(*page_range):
            for item in self.get_page(p):
                if item_range[0] <= counter < item_range[1]:
                    yield self.__schema__.load(item)
                counter += 1
                if counter >= max_item:
                    return StopIteration

    def get_page(self, page_no):
        query = self.query()
        query["recordStartNumber"] = page_no * self.page_size
        response = session.get(self.query_url, params=query)
        return response.json()["results"]

    def __len__(self):
        length = self._len() - self.config["offset"]
        if self.config["limit"]:
            return length if length < self.config["limit"] else self.config["limit"]
        else:
            return length

    def _len(self):
        response = session.get(self.query_url, params=self.query())
        return response.json()["recordTotalQuantity"]

    def query(self):
        query = dict()
        for k, v in self.config["filter"].items():
            key = k if k not in peds_to_ptab else peds_to_ptab[k]
            key = inflection.camelize(key, uppercase_first_letter=False)
            query[key] = " ".join(v)
        query["recordTotalQuantity"] = self.page_size
        query["sortOrderCategory"] = " ".join(
            inflection.camelize(o, uppercase_first_letter=False)
            for o in self.config["order_by"]
        )
        return query

class PtabProceedingManager(PtabManager[PtabProceeding]):
    query_url = "https://developer.uspto.gov/ptab-api/proceedings"
    primary_key = "proceeding_number"
    __schema__ = PtabProceedingSchema()


class PtabDocumentManager(PtabManager[PtabDocument]):
    query_url = "https://developer.uspto.gov/ptab-api/documents"
    primary_key = "document_identifier"
    __schema__ = PtabDocumentSchema()

class PtabDecisionManager(PtabManager[PtabDecision]):
    query_url = "https://developer.uspto.gov/ptab-api/decisions"
    primary_key = "identifier"
    __schema__ = PtabDecisionSchema()