import logging
import typing as tp
from urllib.parse import urljoin

from patent_client._async.http_client import PatentClientSession
from patent_client._async.uspto.ptab.model import (  # ProceedingAggregationOutput,
    PtabDecision,
    PtabDocument,
    PtabProceeding,
    SearchOutput,
)
from patent_client._async.uspto.ptab.schema import (
    DecisionsGetParams,
    DocumentsGetParams,
    ProceedingsGetParams,
    SearchInput,
)

from .errors import PtabApiError

BASE_URL = "https://developer.uspto.gov/ptab-api/"

# Set up logger
logger = logging.getLogger(__name__)


class BaseEndpoint:
    def __init__(self, session: PatentClientSession):
        self.session = session

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        logger.info(
            f"Sending {method.upper()} request to {url}",
            extra={
                "method": method.upper(),
                "url": url,
                "params": kwargs.get("params"),
                "json": kwargs.get("json"),
            },
        )
        response = await getattr(self.session, method.lower())(url, **kwargs)
        response.raise_for_status()
        data = response.json()

        if "responseMessage" in data and "error" in data["responseMessage"].lower():
            raise PtabApiError(f"PTAB API Error: {data['responseMessage']}")

        return data


class ProceedingsEndpoint(BaseEndpoint):
    async def search(self, search_input: SearchInput) -> SearchOutput:
        url = urljoin(BASE_URL, "proceedings/json")
        response_data = await self._request(
            "POST", url, json=search_input.model_dump(by_alias=True, exclude_none=True)
        )
        return SearchOutput(**response_data)

    async def get(self, params: ProceedingsGetParams) -> PtabProceeding:
        url = urljoin(BASE_URL, "proceedings")
        response_data = await self._request("GET", url, params=params.model_dump(exclude_none=True))
        return PtabProceeding(**response_data)


class DocumentsEndpoint(BaseEndpoint):
    async def search(self, search_input: SearchInput) -> SearchOutput:
        url = urljoin(BASE_URL, "documents/json")
        response_data = await self._request(
            "POST", url, json=search_input.model_dump(by_alias=True)
        )
        return SearchOutput(**response_data)

    async def get(self, params: DocumentsGetParams) -> PtabDocument:
        url = urljoin(BASE_URL, "documents")
        response_data = await self._request("GET", url, params=params.model_dump(by_alias=True))
        return PtabDocument(**response_data)

    async def download(self, document_identifier: str) -> bytes:
        url = urljoin(BASE_URL, f"documents/{document_identifier}/download")
        logger.info(
            "Downloading document",
            extra={"method": "GET", "url": url, "document_identifier": document_identifier},
        )
        response = await self.session.get(url)
        response.raise_for_status()
        return response.content

    async def download_trial_documents(self, proceeding_number: str) -> bytes:
        url = urljoin(BASE_URL, f"documents.zip/{proceeding_number}/download")
        logger.info(
            "Downloading trial documents",
            extra={"method": "GET", "url": url, "proceeding_number": proceeding_number},
        )
        response = await self.session.get(url)
        response.raise_for_status()
        return response.content


class DecisionsEndpoint(BaseEndpoint):
    async def search(self, search_input: SearchInput) -> SearchOutput:
        url = urljoin(BASE_URL, "decisions/json")
        response_data = await self._request(
            "POST", url, json=search_input.model_dump(by_alias=True)
        )
        return SearchOutput(**response_data)

    async def get(self, params: DecisionsGetParams) -> PtabDecision:
        url = urljoin(BASE_URL, "decisions")
        response_data = await self._request("GET", url, params=params.model_dump(by_alias=True))
        return PtabDecision(**response_data)


class PtabApiClient:
    def __init__(self, session: tp.Optional[PatentClientSession] = None):
        self.session = session or PatentClientSession()
        self.proceedings = ProceedingsEndpoint(self.session)
        self.documents = DocumentsEndpoint(self.session)
        self.decisions = DecisionsEndpoint(self.session)


ptab_client = PtabApiClient()
