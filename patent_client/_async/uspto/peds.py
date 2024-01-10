import datetime
import logging
import typing as tp

from httpx._exceptions import HTTPStatusError

from ..http_client import PatentClientAsyncHttpClient
from patent_client import function_cache

logger = logging.getLogger(__name__)

type_map = {
    "string": str,
    "date": datetime.datetime,
    "text_general": str,
    "int": int,
    "text_ws": str,
}


class PedsDownException(Exception):
    pass


class PatentExaminationDataSystemApi:
    http_client = PatentClientAsyncHttpClient()
    base_url = "https://ped.uspto.gov/api"
    search_fields: dict = dict()

    @classmethod
    async def _is_online(cls) -> tuple[bool, str]:
        response = await cls.http_client.get(
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

    @classmethod
    async def _check_response(cls, response):
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            alive, reason = await cls._is_online()
            raise e if alive else PedsDownException(reason)

    @classmethod
    @function_cache
    async def get_search_fields(cls) -> dict:
        if hasattr(cls, "search_fields"):
            return cls.search_fields
        response = await cls.http_client.get("https://ped.uspto.gov/api/search-fields")
        await cls()._check_response(response)
        search_fields = response.json()
        cls.search_fields = {k: type_map[v] for k, v in search_fields.items()}
        return cls.search_fields

    @classmethod
    @function_cache
    async def create_query(
        cls,
        query: str,
        query_fields: tp.Optional[str] = None,
        default_field: tp.Optional[str] = "patentTitle",
        facet: bool = False,
        return_fields: tp.Optional[tp.List[str]] = None,
        filter_query: tp.Optional[tp.List[str]] = None,
        minimum_match: str = "100%",
        sort: tp.Optional[str] = "applId asc",
        start: int = 0,
        rows: tp.Optional[int] = None,
    ) -> tp.Any:
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

        params: tp.Dict[str, object] = {
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
        response = await cls.http_client.post(
            url,
            json=params,
            headers={"Accept": "application/json"},
        )
        await cls._check_response(response)
        return response.json()

    @classmethod
    @function_cache
    async def get_documents(cls, appl_id: str) -> tp.Any:
        url = f"https://ped.uspto.gov/api/queries/cms/public/{appl_id}"
        response = await cls.http_client.get(url)
        await cls._check_response(response)
        return response.json()
