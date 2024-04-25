import datetime
import logging
from typing import Dict, List, Optional

from httpx._exceptions import HTTPStatusError

from patent_client._async.http_client import PatentClientSession

from .model import Document, PedsPage

logger = logging.getLogger(__name__)

type_map = {
    "string": str,
    "date": datetime.datetime,
    "text_general": str,
    "int": int,
    "text_ws": str,
}

client = PatentClientSession()


class PedsDownException(Exception):
    pass


class PatentExaminationDataSystemApi:
    base_url = "https://ped.uspto.gov/api"
    search_fields: Dict = dict()

    async def is_online(self) -> bool:
        response = await client.get(
            "https://ped.uspto.gov/api/search-fields",
            extensions={"cache_disabled": True},
        )
        if response.status_code == 200:
            return True, ""
        elif "requested resource is not available" in response.text:
            return False, "Patent Examination Data is Offline - this is a USPTO problem"
        elif "attempt failed or the origin closed the connection" in response.text:
            return (
                False,
                "The Patent Examination Data API is Broken! - this is a USPTO problem",
            )
        else:
            return False, "There is a USPTO problem"

    async def check_response(self, response):
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            alive, reason = await self.is_online()
            raise e if alive else PedsDownException(reason)

    @classmethod
    async def get_search_fields(cls) -> dict:
        if hasattr(cls, "search_fields"):
            return cls.search_fields
        response = await client.get("https://ped.uspto.gov/api/search-fields")
        await cls().check_response(response)
        search_fields = response.json()
        cls.search_fields = {k: type_map[v] for k, v in search_fields.items()}
        return cls.search_fields

    async def create_query(
        self,
        query: str,
        query_fields: Optional[str] = None,
        default_field: Optional[str] = "patentTitle",
        facet: bool = False,
        return_fields: Optional[List[str]] = None,
        filter_query: Optional[List[str]] = None,
        minimum_match: str = "100%",
        sort: Optional[str] = "applId asc",
        start: int = 0,
        rows: Optional[int] = None,
    ) -> "PedsPage":
        """

        Args:
            query (str): The query to be issued to PEDS
            query_fields (str): A list of fields to be queried
            default_field (str, optional): Default field to search. Defaults to None.
            facet (str, optional): Whether to enabled SOLR faceting. Defaults to "false".
            return_fields (str, optional): Specifies which fields should be returned. Defaults to "*".
            filter_query (str, optional)

        Returns:
            _type_: _description_
        """
        if query_fields is None:
            qf = "appEarlyPubNumber applId appLocation appType appStatus_txt appConfrNumber appCustNumber appGrpArtNumber appCls appSubCls appEntityStatus_txt patentNumber patentTitle inventorName firstNamedApplicant appExamName appExamPrefrdName appAttrDockNumber appPCTNumber appIntlPubNumber wipoEarlyPubNumber pctAppType firstInventorFile appClsSubCls rankAndInventorsList".split(
                " "
            )

        params: Dict[str, object] = {
            "df": default_field,
            "qf": " ".join(qf),
            "fl": " ".join(return_fields) if return_fields else "*",
            "fq": filter_query if filter_query else list(),
            "searchText": query,
            "sort": sort,
            "facet": "true" if facet else "false",
            "mm": minimum_match,
            "start": str(start),
        }
        if rows:
            params["rows"] = rows
        url = "https://ped.uspto.gov/api/queries"
        logger.debug(f"POST {url}\n{params}")
        response = await client.post(
            url,
            json=params,
            headers={"Accept": "application/json"},
        )
        await self.check_response(response)
        return PedsPage.model_validate(response.json())

    async def get_documents(self, appl_id: str) -> List[Document]:
        url = f"https://ped.uspto.gov/api/queries/cms/public/{appl_id}"
        response = await client.get(url)
        await self.check_response(response)
        return [Document.model_validate(d) for d in response.json()]
