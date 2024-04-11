from typing import Iterator, TYPE_CHECKING
from patent_client.util.manager import Manager
from patent_client.util.request_util import get_start_and_row_count
from .api import ODPApi
from .model.api_models import SearchRequest
from .query import create_post_search_obj

if TYPE_CHECKING:
    from .model.data_models import USApplication, ApplicationBiblio, Document, Continuity


api = ODPApi()

class USApplicationManager(Manager):
    default_filter = "appl_id"
    
    def _len(self):
        return api.post_search(self._create_search_obj()).count
    
    def _get_results(self) -> Iterator["USApplication"]:
        query_obj = self._create_search_obj()
        for start, rows in get_start_and_row_count(self.config.limit):
            page_query = query_obj.model_dump()
            page_query['pagination'] = {"offset": start, "limit": rows}
            page_query_obj = SearchRequest(**page_query)
            for result in api.post_search(page_query_obj).results:
                yield result
        
    def _create_search_obj(self):
        if "query" in self.config.filter:
            return SearchRequest(**self.config.filter["query"][0])
        elif "q" in self.config.filter:
            return SearchRequest(q=self.config.filter["q"][0])
        else:
            return create_post_search_obj(self.config)

class AttributeManager(Manager):
    def filter(self, *args, **kwargs):
        raise NotImplementedError("Filtering attributes is not supported")
    
    def get(self, *args, **kwargs):
        raise NotImplementedError("Getting attributes is not supported")
    
    def limit(self, *args, **kwargs):
        raise NotImplementedError("Limit is not supported")
    
    def offset(self, *args, **kwargs):
        raise NotImplementedError("Offset is not supported")
        
class ApplicationBiblioManager(AttributeManager):
    
    def get(self, appl_id: str) -> "ApplicationBiblio":
        return api.get_application_biblio_data(appl_id)
    
class ApplicationManager(AttributeManager):
    
    def get(self, appl_id: str) -> "USApplication":
        return api.get_application_data(appl_id)
    
class ContinuityManager(AttributeManager):
    
    def get(self, appl_id:str) -> "Continuity":
        return api.get_continuity_data(appl_id)
    
class DocumentManager(Manager):
    default_filter = "appl_id"
    
    def _len(self):
        return len(api.get_documents(self.config.filter["appl_id"][0]))
    
    def _get_results(self) -> Iterator["Document"]:
        for doc in api.get_documents(self.config.filter["appl_id"][0]):
            yield doc

            
        

            

