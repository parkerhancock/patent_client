import httpx
import requests
from patent_client import SETTINGS
import typing as tp


from .model import SearchRequest, SearchGetRequest,SearchResponse, Application, ApplicationBiblio, TermAdjustment, Assignment, CustomerNumber, Continuity, ForeignPriority, Transaction, Document


def prune(obj: tp.Any) -> tp.Any:
    if isinstance(obj, dict):
        return {k: prune(v) for k, v in obj.items() if v is not None and not (isinstance(v, tp.Collection) and len(v) == 0)}
    elif isinstance(obj, list):
        return [prune(v) for v in obj if v is not None and not (isinstance(v, tp.Collection) and len(v) == 0)]
    else:
        return obj

class ODPApi:
    base_url = "https://beta-api.uspto.gov"
    def __init__(self):
        #self.client = httpx.Client(follow_redirects=True, headers={"X-API-KEY": SETTINGS.odp_api_key})
        self.client = requests.Session()
        self.client.headers['X-API-KEY'] = SETTINGS.odp_api_key

    def post_search(self, search_request: SearchRequest = SearchRequest()) -> SearchResponse:
        url = self.base_url + "/api/v1/patent/applications/search"
        search_data = prune(search_request.model_dump())
        response = self.client.post(url, json=search_data, headers={"accept": "application/json"})
        response.raise_for_status()
        return SearchResponse(**response.json())

    def get_search(self, search_request: SearchGetRequest = SearchGetRequest()) -> SearchResponse:
        """Patent application search by supplying query parameters
        Query parameters are optional. When no query parameters supplied, top 25 applications are returned"""
        url = self.base_url + "/api/v1/patent/applications/search"
        search_data = prune(search_request.model_dump())
        response = self.client.get(url, params=search_data)
        response.raise_for_status()
        return SearchResponse(**response.json())
    
    # Data Attributes
    
    def get_application_data(self, application_id: str) -> Application:
        """Patent application data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}"
        response = self.client.get(url)
        response.raise_for_status()
        return Application(**response.json()['patentBag'][0])
    
    def get_application_biblio_data(self, application_id: str) -> ApplicationBiblio:
        """Patent application basic data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/application-data"
        response = self.client.get(url)
        response.raise_for_status()
        return ApplicationBiblio(**response.json()['patentBag'][0])
    
    def get_patent_term_adjustment_data(self, application_id: str) -> TermAdjustment:
        """Patent application term adjustment data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/adjustment"
        response = self.client.get(url)
        response.raise_for_status()
        return TermAdjustment(**response.json()['patentBag'][0]['patentTermAdjustmentData'])
    
    def get_assignments(self, application_id: str) -> tp.List[Assignment]:
        """Patent application term adjustment data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/assignment"
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()["patentBag"][0]['assignmentBag']
        return [Assignment(**assignment) for assignment in data]
    
    def get_attorney_data(self, application_id: str) -> CustomerNumber:
        """Patent application attorney data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/attorney"
        response = self.client.get(url)
        response.raise_for_status()
        return CustomerNumber(**response.json()['patentBag'][0]['recordAttorney'])
    
    def get_continuity_data(self, application_id: str) -> Continuity:
        """Patent application continuity data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/continuity"
        response = self.client.get(url)
        response.raise_for_status()
        return Continuity(**response.json())
    
    def get_foreign_priority_data(self, application_id: str) -> tp.List[ForeignPriority]:
        """Patent application foreign priority data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/foreign-priority"
        response = self.client.get(url)
        response.raise_for_status()
        return [ForeignPriority(**foreign_priority) for foreign_priority in response.json()['patentBag'][0]['foreignPriorityBag']]
    
    def get_transactions(self, application_id: str) -> tp.List[Transaction]:
        """Patent application transactions by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/transactions"
        response = self.client.get(url)
        response.raise_for_status()
        return [Transaction(**transaction) for transaction in response.json()['patentBag'][0]['transactionContentBag']]

    def get_documents(self, application_id: str) -> tp.List[Document]:
        """Patent application documents by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/documents"
        response = self.client.get(url)
        response.raise_for_status()
        return [Document(**document) for document in response.json()['documentBag']]

