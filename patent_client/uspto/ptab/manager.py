from copy import deepcopy
from typing import Callable
from typing import Generic
from typing import Optional

import inflection

from .model import PtabDecision
from .model import PtabDecisionPage
from .model import PtabDocument
from .model import PtabDocumentPage
from .model import PtabProceeding
from .model import PtabProceedingPage
from .util import peds_to_ptab
from patent_client._async.uspto.ptab import PtabApi as PtabAsyncApi
from patent_client._sync.uspto.ptab import PtabApi as PtabSyncApi
from patent_client.util.manager import Manager
from patent_client.util.manager import ModelType
from patent_client.util.request_util import get_start_and_row_count


class PtabManager(Manager, Generic[ModelType]):
    url = "https://developer.uspto.gov/ptab-api"
    page_size = 25
    instance_schema = None
    api_method: Optional[Callable] = None

    def _get_results(self):
        api_func = getattr(PtabSyncApi, self.api_method)
        query = deepcopy(self.config.filter)
        query = peds_to_ptab(query)
        query["sort"] = " ".join(inflection.camelize(o, uppercase_first_letter=False) for o in self.config.order_by)
        for start, rows in get_start_and_row_count(self.config.limit, self.config.offset, self.page_size):
            query["start"] = start
            query["rows"] = rows
            data = api_func(**query)
            page = self.output_model_page.model_validate(data)
            for doc in page.docs:
                yield doc
            if len(page.docs) < rows:
                break

    def len(self):
        api_func = getattr(PtabSyncApi, self.api_method)
        data = api_func(**peds_to_ptab(self.config.filter))
        page = self.output_model_page.model_validate(data)
        return min(self.config.limit, page.num_found) if self.config.limit else page.num_found

    async def _aget_results(self):
        api_func = getattr(PtabAsyncApi, self.api_method)
        query = deepcopy(self.config.filter)
        query = peds_to_ptab(query)
        query["sort"] = " ".join(inflection.camelize(o, uppercase_first_letter=False) for o in self.config.order_by)
        for start, rows in get_start_and_row_count(self.config.limit, self.config.offset, self.page_size):
            query["start"] = start
            query["rows"] = rows
            data = await api_func(**query)
            page = self.output_model_page.model_validate(data)
            for doc in page.docs:
                yield doc
            if len(page.docs) < rows:
                break

    async def alen(self):
        api_func = getattr(PtabAsyncApi, self.api_method)
        data = await api_func(**peds_to_ptab(self.config.filter))
        page = self.output_model_page.model_validate(data)
        return min(self.config.limit, page.num_found) if self.config.limit else page.num_found


class PtabProceedingManager(PtabManager[PtabProceeding]):
    path = "/proceedings"
    default_filter = "proceeding_number"
    api_method = "get_proceedings"
    output_model_page = PtabProceedingPage


class PtabDocumentManager(PtabManager[PtabDocument]):
    path = "/documents"
    default_filter = "document_identifier"
    api_method = "get_documents"
    output_model_page = PtabDocumentPage


class PtabDecisionManager(PtabManager[PtabDecision]):
    path = "/decisions"
    default_filter = "identifier"
    api_method = "get_decisions"
    output_model_page = PtabDecisionPage
