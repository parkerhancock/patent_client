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


def _merge_application_metadata(entry: dict) -> dict:
    combined: dict = dict(entry)
    app_meta = combined.pop("applicationMetaData", {}) or {}
    entity_status = app_meta.pop("entityStatusData", {}) or {}
    # flatten entity status details
    business_status = entity_status.get("businessEntityStatusCategory")
    if business_status is not None:
        combined.setdefault("businessEntityStatusCategory", business_status)
    small_entity = entity_status.get("smallEntityStatusIndicator")
    if small_entity is not None:
        combined.setdefault("smallEntityStatusIndicator", small_entity)

    for key, value in app_meta.items():
        combined.setdefault(key, value)

    # continuity data arrives as separate bags
    parent = combined.pop("parentContinuityBag", None)
    child = combined.pop("childContinuityBag", None)
    if parent is not None or child is not None:
        combined["continuityBag"] = {
            "parentContinuityBag": parent or [],
            "childContinuityBag": child or [],
        }

    return combined


def _normalize_patent_response(data: dict) -> dict:
    bag = [_merge_application_metadata(entry) for entry in data.get("patentFileWrapperDataBag", [])]
    return {
        "count": data.get("count", len(bag)),
        "patentBag": bag,
        "requestIdentifier": data.get("requestIdentifier"),
    }


class ODPApi:
    base_url = "https://api.uspto.gov"

    def __init__(self):
        if SETTINGS.odp_api_key is None:
            raise ValueError("ODP API key is not set")
        self.client = PatentClientSession(headers={"X-API-KEY": SETTINGS.odp_api_key})

    async def post_search(self, search_request: SearchRequest = SearchRequest()) -> tp.Dict:
        url = self.base_url + "/api/v1/patent/applications/search"
        search_data = prune(search_request.model_dump())
        response = await self.client.post(
            url, json=search_data, headers={"accept": "application/json"}
        )
        if response.status_code == 404 and "No matching records found" in response.text:
            data = response.json()
            data.setdefault("patentFileWrapperDataBag", [])
            data.setdefault("count", 0)
            return _normalize_patent_response(data)
        response.raise_for_status()
        return _normalize_patent_response(response.json())

    async def get_search(self, search_request: SearchGetRequest = SearchGetRequest()) -> tp.Dict:
        """Patent application search by supplying query parameters
        Query parameters are optional. When no query parameters supplied, top 25 applications are returned"""
        url = self.base_url + "/api/v1/patent/applications/search"
        search_data = prune(search_request.model_dump())
        response = await self.client.get(url, params=search_data)
        if response.status_code == 404 and "No matching records found" in response.text:
            data = response.json()
            data.setdefault("patentFileWrapperDataBag", [])
            data.setdefault("count", 0)
            return _normalize_patent_response(data)
        response.raise_for_status()
        return _normalize_patent_response(response.json())

    # Data Attributes

    async def get_application_data(self, application_id: str) -> USApplication:
        """Patent application data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}"
        response = await self.client.get(url)
        response.raise_for_status()
        data = _normalize_patent_response(response.json())
        return USApplication(**data["patentBag"][0])

    async def get_application_biblio_data(self, application_id: str) -> USApplicationBiblio:
        """Patent application basic data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}"
        response = await self.client.get(url)
        response.raise_for_status()
        data = _normalize_patent_response(response.json())
        return USApplicationBiblio(**data["patentBag"][0])

    async def get_patent_term_adjustment_data(self, application_id: str) -> TermAdjustment:
        """Patent application term adjustment data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/adjustment"
        response = await self.client.get(url)
        response.raise_for_status()
        data = _normalize_patent_response(response.json())
        return TermAdjustment(**data["patentBag"][0]["patentTermAdjustmentData"])

    async def get_assignments(self, application_id: str) -> tp.List[Assignment]:
        """Patent application term adjustment data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/assignment"
        response = await self.client.get(url)
        response.raise_for_status()
        data = _normalize_patent_response(response.json())
        assignments = data["patentBag"][0].get("assignmentBag", [])
        return [Assignment(**assignment) for assignment in assignments]

    async def get_attorney_data(self, application_id: str) -> CustomerNumber:
        """Patent application attorney data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/attorney"
        response = await self.client.get(url)
        response.raise_for_status()
        data = _normalize_patent_response(response.json())
        return CustomerNumber(**data["patentBag"][0]["recordAttorney"])

    async def get_continuity_data(self, application_id: str) -> Continuity:
        """Patent application continuity data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/continuity"
        response = await self.client.get(url)
        response.raise_for_status()
        return Continuity(**_normalize_patent_response(response.json()))

    async def get_foreign_priority_data(self, application_id: str) -> tp.List[ForeignPriority]:
        """Patent application foreign priority data by application id"""
        url = (
            self.base_url
            + f"/api/v1/patent/applications/{urlescape(application_id)}/foreign-priority"
        )
        response = await self.client.get(url)
        response.raise_for_status()
        data = _normalize_patent_response(response.json())
        return [
            ForeignPriority(**foreign_priority)
            for foreign_priority in data["patentBag"][0].get("foreignPriorityBag", [])
        ]

    async def get_transactions(self, application_id: str) -> tp.List[Transaction]:
        """Patent application transactions by application id"""
        url = (
            self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/transactions"
        )
        response = await self.client.get(url)
        response.raise_for_status()
        data = _normalize_patent_response(response.json())
        return [
            Transaction(**transaction)
            for transaction in data["patentBag"][0].get("transactionContentBag", [])
        ]

    async def get_documents(self, application_id: str) -> tp.List[Document]:
        """Patent application documents by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/documents"
        response = await self.client.get(url)
        response.raise_for_status()
        return [Document(**document) for document in response.json()["documentBag"]]
