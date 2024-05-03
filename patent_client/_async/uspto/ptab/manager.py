from copy import deepcopy
from typing import Callable, Generic, Optional

import inflection

from patent_client.util.manager import AsyncManager, ModelType
from patent_client.util.request_util import get_start_and_row_count

from .api import PtabApi
from .model import PtabDecision, PtabDocument, PtabProceeding
from .util import peds_to_ptab


class PtabManager(AsyncManager, Generic[ModelType]):
    url = "https://developer.uspto.gov/ptab-api"
    page_size = 25
    instance_schema = None
    api_method: Optional[Callable] = None

    async def _get_results(self):
        query = deepcopy(self.config.filter)
        query = peds_to_ptab(query)
        query["sort"] = " ".join(
            inflection.camelize(o, uppercase_first_letter=False) for o in self.config.order_by
        )
        for start, rows in get_start_and_row_count(
            self.config.limit, self.config.offset, self.page_size
        ):
            query["start"] = start
            query["rows"] = rows
            page = await self.api_method(**query)
            for doc in page.docs:
                yield doc
            if len(page.docs) < rows:
                break

    async def count(self):
        page = await self.api_method(**peds_to_ptab(self.config.filter))
        return min(self.config.limit, page.num_found) if self.config.limit else page.num_found

    # def allowed_filters(self):
    #    params = schema_doc["paths"][self.path]["get"]["parameters"]
    #    return {inflection.underscore(p["name"]): p["description"] for p in params}


class PtabProceedingManager(PtabManager[PtabProceeding]):
    path = "/proceedings"
    default_filter = "proceeding_number"
    api_method = PtabApi.get_proceedings


class PtabDocumentManager(PtabManager[PtabDocument]):
    path = "/documents"
    default_filter = "document_identifier"
    api_method = PtabApi.get_documents


class PtabDecisionManager(PtabManager[PtabDecision]):
    path = "/decisions"
    default_filter = "identifier"
    api_method = PtabApi.get_decisions
