import math
from typing import Generic

import inflection
from patent_client.util import Manager
from patent_client.util import ModelType

from . import schema_doc
from . import session
from .model import PtabDecision
from .model import PtabDocument
from .model import PtabProceeding
from .schema import PtabDecisionSchema
from .schema import PtabDocumentSchema
from .schema import PtabProceedingSchema
from .util import peds_to_ptab


class PtabManager(Manager, Generic[ModelType]):
    url = "https://developer.uspto.gov/ptab-api"
    page_size = 25
    instance_schema = None

    def _get_results(self):
        total = self._len()
        offset = self.config.offset
        limit = self.config.limit
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
        response = session.get(self.url + self.path, params=query)
        return response.json()["results"]

    def __len__(self):
        length = self._len() - self.config.offset
        if self.config.limit:
            return length if length < self.config.limit else self.config.limit
        else:
            return length

    def _len(self):
        response = session.get(self.url + self.path, params=self.query())
        return response.json()["recordTotalQuantity"]

    def query(self):
        query = dict()
        for k, v in self.config.filter.items():
            key = k if k not in peds_to_ptab else peds_to_ptab[k]
            key = inflection.camelize(key, uppercase_first_letter=False)
            if isinstance(v, list):
                query[key] = " ".join(v)
            else:
                query[key] = v
        query["recordTotalQuantity"] = self.page_size
        query["sortOrderCategory"] = " ".join(
            inflection.camelize(o, uppercase_first_letter=False) for o in self.config.order_by
        )
        return query

    def allowed_filters(self):
        params = schema_doc["paths"][self.path]["get"]["parameters"]
        return {inflection.underscore(p["name"]): p["description"] for p in params}


class PtabProceedingManager(PtabManager[PtabProceeding]):
    path = "/proceedings"
    primary_key = "proceeding_number"
    __schema__ = PtabProceedingSchema()


class PtabDocumentManager(PtabManager[PtabDocument]):
    path = "/documents"
    primary_key = "document_identifier"
    __schema__ = PtabDocumentSchema()


class PtabDecisionManager(PtabManager[PtabDecision]):
    path = "/decisions"
    primary_key = "identifier"
    __schema__ = PtabDecisionSchema()
