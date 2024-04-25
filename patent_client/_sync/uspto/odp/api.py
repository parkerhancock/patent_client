# ********************************************************************************
# *         WARNING: This file is automatically generated by unasync.py.         *
# *                             DO NOT MANUALLY EDIT                             *
# *              Source File: patent_client/_async/uspto/odp/api.py              *
# ********************************************************************************

import typing as tp

import httpx

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


class ODPApi:
    base_url = "https://beta-api.uspto.gov"

    def __init__(self):
        self.client = PatentClientSession(
            headers={"X-API-KEY": SETTINGS.odp_api_key}
        )

    def post_search(
        self, search_request: SearchRequest = SearchRequest()
    ) -> tp.Dict:
        url = self.base_url + "/api/v1/patent/applications/search"
        search_data = prune(search_request.model_dump())
        response = self.client.post(
            url, json=search_data, headers={"accept": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    def get_search(
        self, search_request: SearchGetRequest = SearchGetRequest()
    ) -> tp.Dict:
        """Patent application search by supplying query parameters
        Query parameters are optional. When no query parameters supplied, top 25 applications are returned"""
        url = self.base_url + "/api/v1/patent/applications/search"
        search_data = prune(search_request.model_dump())
        response = self.client.get(url, params=search_data)
        response.raise_for_status()
        return response.json()

    # Data Attributes

    def get_application_data(self, application_id: str) -> USApplication:
        """Patent application data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}"
        response = self.client.get(url)
        response.raise_for_status()
        return USApplication(**response.json()["patentBag"][0])

    def get_application_biblio_data(
        self, application_id: str
    ) -> USApplicationBiblio:
        """Patent application basic data by application id"""
        url = (
            self.base_url
            + f"/api/v1/patent/applications/{application_id}/application-data"
        )
        response = self.client.get(url)
        response.raise_for_status()
        return USApplicationBiblio(**response.json()["patentBag"][0])

    def get_patent_term_adjustment_data(
        self, application_id: str
    ) -> TermAdjustment:
        """Patent application term adjustment data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/adjustment"
        response = self.client.get(url)
        response.raise_for_status()
        return TermAdjustment(
            **response.json()["patentBag"][0]["patentTermAdjustmentData"]
        )

    def get_assignments(self, application_id: str) -> tp.List[Assignment]:
        """Patent application term adjustment data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/assignment"
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()["patentBag"][0]["assignmentBag"]
        return [Assignment(**assignment) for assignment in data]

    def get_attorney_data(self, application_id: str) -> CustomerNumber:
        """Patent application attorney data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/attorney"
        response = self.client.get(url)
        response.raise_for_status()
        return CustomerNumber(**response.json()["patentBag"][0]["recordAttorney"])

    def get_continuity_data(self, application_id: str) -> Continuity:
        """Patent application continuity data by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/continuity"
        response = self.client.get(url)
        response.raise_for_status()
        return Continuity(**response.json())

    def get_foreign_priority_data(
        self, application_id: str
    ) -> tp.List[ForeignPriority]:
        """Patent application foreign priority data by application id"""
        url = (
            self.base_url
            + f"/api/v1/patent/applications/{application_id}/foreign-priority"
        )
        response = self.client.get(url)
        response.raise_for_status()
        return [
            ForeignPriority(**foreign_priority)
            for foreign_priority in response.json()["patentBag"][0][
                "foreignPriorityBag"
            ]
        ]

    def get_transactions(self, application_id: str) -> tp.List[Transaction]:
        """Patent application transactions by application id"""
        url = (
            self.base_url + f"/api/v1/patent/applications/{application_id}/transactions"
        )
        response = self.client.get(url)
        response.raise_for_status()
        return [
            Transaction(**transaction)
            for transaction in response.json()["patentBag"][0]["transactionContentBag"]
        ]

    def get_documents(self, application_id: str) -> tp.List[Document]:
        """Patent application documents by application id"""
        url = self.base_url + f"/api/v1/patent/applications/{application_id}/documents"
        response = self.client.get(url)
        response.raise_for_status()
        return [Document(**document) for document in response.json()["documentBag"]]