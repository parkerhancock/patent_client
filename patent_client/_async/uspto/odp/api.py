import typing as tp
from urllib.parse import quote


from patent_client import SETTINGS

from ...http_client import PatentClientSession
from .model import (
    Assignment,
    BdssResponseBag,
    BdssResponseProductBag,
    DocumentBag,
    EventData,
    ForeignPriority,
    PatentDataResponse,
    PatentDownloadRequest,
    PatentFileWrapperDataBagItem,
    PatentSearchRequest,
    StatusCodeSearchResponse,
)

def urlescape(s: str) -> str:
    return quote(s, safe="")

class ODPApi:
    """USPTO Open Data Portal API client."""

    def __init__(self, api_key: tp.Optional[str] = None):
        if api_key is None and SETTINGS.odp_api_key is None:
            raise ValueError("ODP API key is not set")
        self.client = PatentClientSession(headers={"X-API-KEY": api_key or SETTINGS.odp_api_key})
        self.patent_search = self.PatentSearch(self.client)
        self.bulk_data = self.BulkDataSets(self.client)

    class PatentSearch:
        """Patent search and data retrieval endpoints."""

        base_url = "https://beta-api.uspto.gov"

        def __init__(self, client: PatentClientSession):
            self.client = client

        async def post_search(self, search_request: PatentSearchRequest = PatentSearchRequest()) -> tp.Dict:
            url = self.base_url + "/api/v1/patent/applications/search"
            search_data = search_request.model_dump(by_alias=True, exclude_unset=True)
            print("Search request data:", search_data)  # Debug logging
            try:
                response = await self.client.post(
                    url, json=search_data, headers={"accept": "application/json"}
                )
            except TypeError:
                breakpoint()
            if response.status_code == 404 and "No matching records found" in response.text:
                return {
                    "count": 0,
                    "patentFileWrapperDataBag": [],
                    "requestIdentifier": response.json()["requestIdentifier"],
                }
            if response.status_code == 400:
                print("Response text:", response.text)  # Debug logging for error response
            response.raise_for_status()
            return response.json()

        async def get_search(self, search_request: PatentSearchRequest = PatentSearchRequest()) -> tp.Dict:
            """Patent application search by supplying query parameters
            Query parameters are optional. When no query parameters supplied, top 25 applications are returned"""
            url = self.base_url + "/api/v1/patent/applications/search"
            search_data = search_request.model_dump(by_alias=True, exclude_unset=True)
            response = await self.client.get(url, params=search_data)
            if response.status_code == 404 and "No matching records found" in response.text:
                return {
                    "count": 0,
                    "patentFileWrapperDataBag": [],
                    "requestIdentifier": response.json()["requestIdentifier"],
                }
            response.raise_for_status()
            return response.json()

        async def get_application_data(self, application_id: str) -> PatentFileWrapperDataBagItem:
            """Patent application data by application id"""
            url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}"
            response = await self.client.get(url)
            response.raise_for_status()
            return PatentFileWrapperDataBagItem(**response.json()["patentFileWrapperDataBag"][0])

        async def get_application_biblio_data(self, application_id: str) -> PatentFileWrapperDataBagItem:
            """Patent application basic data by application id"""
            url = (
                self.base_url
                + f"/api/v1/patent/applications/{urlescape(application_id)}/meta-data"
            )
            response = await self.client.get(url)
            response.raise_for_status()
            return PatentFileWrapperDataBagItem(**response.json()["patentFileWrapperDataBag"][0])

        async def get_patent_term_adjustment_data(self, application_id: str) -> PatentFileWrapperDataBagItem:
            """Patent application term adjustment data by application id"""
            url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/adjustment"
            response = await self.client.get(url)
            response.raise_for_status()
            return PatentFileWrapperDataBagItem(**response.json()["patentFileWrapperDataBag"][0])

        async def get_assignments(self, application_id: str) -> tp.List[Assignment]:
            """Patent application term adjustment data by application id"""
            url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/assignment"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()["patentFileWrapperDataBag"][0]["assignmentBag"]
            return [Assignment(**assignment) for assignment in data]

        async def get_attorney_data(self, application_id: str) -> PatentFileWrapperDataBagItem:
            """Patent application attorney data by application id"""
            url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/attorney"
            response = await self.client.get(url)
            response.raise_for_status()
            return PatentFileWrapperDataBagItem(**response.json()["patentFileWrapperDataBag"][0])

        async def get_continuity_data(self, application_id: str) -> PatentDataResponse:
            """Patent application continuity data by application id"""
            url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/continuity"
            response = await self.client.get(url)
            response.raise_for_status()
            return PatentDataResponse(**response.json())

        async def get_foreign_priority_data(self, application_id: str) -> tp.List[ForeignPriority]:
            """Patent application foreign priority data by application id"""
            url = (
                self.base_url
                + f"/api/v1/patent/applications/{urlescape(application_id)}/foreign-priority"
            )
            response = await self.client.get(url)
            response.raise_for_status()
            return [
                ForeignPriority(**foreign_priority)
                for foreign_priority in response.json()["patentFileWrapperDataBag"][0]["foreignPriorityBag"]
            ]

        async def get_transactions(self, application_id: str) -> tp.List[EventData]:
            """Patent application transactions by application id"""
            url = (
                self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/transactions"
            )
            response = await self.client.get(url)
            response.raise_for_status()
            return [
                EventData(**transaction)
                for transaction in response.json()["patentFileWrapperDataBag"][0]["eventDataBag"]
            ]

        async def get_documents(self, application_id: str) -> DocumentBag:
            """Patent application documents by application id"""
            url = self.base_url + f"/api/v1/patent/applications/{urlescape(application_id)}/documents"
            response = await self.client.get(url)
            response.raise_for_status()
            return DocumentBag(**response.json())

    class BulkDataSets:
        """Bulk dataset directory endpoints."""

        base_url = "https://beta-api.uspto.gov"

        def __init__(self, client: PatentClientSession):
            self.client = client

        async def get_search(
            self,
            q: tp.Optional[str] = None,
            product_title: tp.Optional[str] = None,
            product_description: tp.Optional[str] = None,
            product_short_name: tp.Optional[str] = None,
            offset: int = 0,
            limit: int = 10,
            facets: bool = False,
            include_files: bool = True,
            latest: bool = False,
            labels: tp.Optional[str] = None,
            categories: tp.Optional[str] = None,
            datasets: tp.Optional[str] = None,
            file_types: tp.Optional[str] = None,
        ) -> BdssResponseBag:
            """Search bulk datasets products by supplying query parameters."""
            url = self.base_url + "/api/v1/datasets/products/search"
            params = {
                "q": q,
                "productTitle": product_title,
                "productDescription": product_description,
                "productShortName": product_short_name,
                "offset": offset,
                "limit": limit,
                "facets": str(facets).lower(),
                "includeFiles": str(include_files).lower(),
                "latest": str(latest).lower(),
                "labels": labels,
                "categories": categories,
                "datasets": datasets,
                "fileTypes": file_types,
            }
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return BdssResponseBag(**response.json())

        async def get_product(
            self,
            product_identifier: str,
            file_data_from_date: tp.Optional[str] = None,
            file_data_to_date: tp.Optional[str] = None,
            offset: tp.Optional[int] = None,
            limit: tp.Optional[int] = None,
            include_files: bool = True,
            latest: bool = False,
        ) -> BdssResponseProductBag:
            """Find a product by its identifier (shortName)."""
            url = self.base_url + f"/api/v1/datasets/products/{urlescape(product_identifier)}"
            params = {
                "fileDataFromDate": file_data_from_date,
                "fileDataToDate": file_data_to_date,
                "offset": offset,
                "limit": limit,
                "includeFiles": str(include_files).lower(),
                "latest": str(latest).lower(),
            }
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return BdssResponseProductBag(**response.json())
