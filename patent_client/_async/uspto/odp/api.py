import asyncio
import time
import typing as tp
from urllib.parse import quote

from patent_client import SETTINGS

from ...http_client import PatentClientSession
from .model import (
    Assignment,
    Continuity,
    CustomerNumber,
    Document,
    ForeignPriority,
    SearchGetRequest,
    SearchRequest,
    TermAdjustment,
    Transaction,
    USApplication,
    USApplicationBiblio,
)
from .util import prune


def urlescape(s: str) -> str:
    return quote(s, safe="")


class ODPApi:
    base_url = "https://beta-api.uspto.gov"
    time_between_requests = 0.1

    def __init__(self):
        if SETTINGS.odp_api_key is None:
            raise ValueError("ODP API key is not set")
        self.client = PatentClientSession(headers={"X-API-KEY": SETTINGS.odp_api_key})
        self.last_request_time = None

    async def _do_request(self, *args, **kwargs):
        time_since_last_request = (
            time.time() - self.last_request_time if self.last_request_time else 2
        )
        if time_since_last_request < self.time_between_requests:
            await asyncio.sleep(self.time_between_requests - time_since_last_request)
        response = await self.client.request(*args, **kwargs)
        self.last_request_time = time.time()
        return response

    async def post_search(self, search_request: SearchRequest = SearchRequest()) -> tp.Dict:
        url = self.base_url + "/api/v1/patent/applications/search"
        search_data = search_request.model_dump()
        response = await self._do_request(
            "POST", url, json=search_data, headers={"accept": "application/json"}
        )
        if response.status_code == 404 and "No matching records found" in response.text:
            return {
                "count": 0,
                "patentFileWrapperDataBag": [],
                "requestIdentifier": response.json()["requestIdentifier"],
            }
        response.raise_for_status()
        return response.json()

    async def get_search(self, search_request: SearchGetRequest = SearchGetRequest()) -> tp.Dict:
        """Patent application search by supplying query parameters
        Query parameters are optional. When no query parameters supplied, top 25 applications are returned"""
        url = self.base_url + "/api/v1/patent/applications/search"
        search_data = prune(search_request.model_dump())
        response = await self._do_request("GET", url, params=search_data)
        if response.status_code == 404 and "No matching records found" in response.text:
            return {
                "count": 0,
                "patentFileWrapperDataBag": [],
                "requestIdentifier": response.json()["requestIdentifier"],
            }
        response.raise_for_status()
        return response.json()

    # Data Attributes

    async def get_application_data(self, application_id: str) -> USApplication:
        """Patent application data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}"
        response = await self._do_request("GET", url)
        response.raise_for_status()
        return USApplication(**response.json()["patentFileWrapperDataBag"][0])

    async def get_application_biblio_data(self, application_id: str) -> USApplicationBiblio:
        """Patent application basic data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/meta-data"
        response = await self._do_request("GET", url)
        response.raise_for_status()
        return USApplicationBiblio(**response.json()["patentFileWrapperDataBag"][0])

    async def get_patent_term_adjustment_data(self, application_id: str) -> TermAdjustment:
        """Patent application term adjustment data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/adjustment"
        response = await self._do_request("GET", url)
        response.raise_for_status()
        return TermAdjustment(
            **response.json()["patentFileWrapperDataBag"][0]["patentTermAdjustmentData"]
        )

    async def get_assignments(self, application_id: str) -> tp.List[Assignment]:
        """Patent application term adjustment data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/assignment"
        response = await self._do_request("GET", url)
        response.raise_for_status()
        data = response.json()["patentFileWrapperDataBag"][0]["assignmentBag"]
        return [Assignment(**assignment) for assignment in data]

    async def get_attorney_data(self, application_id: str) -> CustomerNumber:
        """Patent application attorney data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/attorney"
        response = await self._do_request("GET", url)
        response.raise_for_status()
        return CustomerNumber(**response.json()["patentFileWrapperDataBag"][0]["recordAttorney"])

    async def get_continuity_data(self, application_id: str) -> Continuity:
        """Patent application continuity data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/continuity"
        response = await self._do_request("GET", url)
        response.raise_for_status()
        return Continuity(**response.json())

    async def get_foreign_priority_data(self, application_id: str) -> tp.List[ForeignPriority]:
        """Patent application foreign priority data by application id"""
        url = (
            self.base_url
            + f"/api/v1/patent/applications/{urlescape(application_id)}/foreign-priority"
        )
        response = await self._do_request("GET", url)
        response.raise_for_status()
        return [
            ForeignPriority(**foreign_priority)
            for foreign_priority in response.json()["patentFileWrapperDataBag"][0][
                "foreignPriorityBag"
            ]
        ]

    async def get_transactions(self, application_id: str) -> tp.List[Transaction]:
        """Patent application transactions by application id"""
        url = (
            self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/transactions"
        )
        response = await self._do_request("GET", url)
        response.raise_for_status()
        return [
            Transaction(**transaction)
            for transaction in response.json()["patentFileWrapperDataBag"][0]["eventDataBag"]
        ]

    async def get_documents(self, application_id: str) -> tp.List[Document]:
        """Patent application documents by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/documents"
        response = await self._do_request("GET", url)
        response.raise_for_status()
        return [Document(**document) for document in response.json()["documentBag"]]
