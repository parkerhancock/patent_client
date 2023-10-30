import datetime
import json
from typing import List
from typing import Optional

from .model import PedsPage
from .schema import PedsPageSchema
from .session import session

type_map = {
    "string": str,
    "date": datetime.datetime,
    "text_general": str,
    "int": int,
    "text_ws": str,
}


class NotAvailableException(Exception):
    pass


class PatentExaminationDataSystemApi:
    base_url = "https://ped.uspto.gov/api"

    def __init__(self):
        query_id = None

    @classmethod
    async def is_online(cls) -> bool:
        response = await session.get("https://ped.uspto.gov/api/search-fields")
        if response.status_code == 200:
            return True
        elif "requested resource is not available" in response.text:
            raise NotAvailableException("Patent Examination Data is Offline - this is a USPTO problem")
        elif "attempt failed or the origin closed the connection" in response.text:
            raise NotAvailableException("The Patent Examination Data API is Broken! - this is a USPTO problem")
        else:
            raise NotAvailableException("There is a USPTO problem")

    @classmethod
    async def get_search_fields(cls) -> dict:
        if hasattr(cls, "search_fields"):
            return cls.search_fields
        response = await session.get("https://ped.uspto.gov/api/search-fields")
        response.raise_for_status()
        search_fields = response.json()
        cls.search_fields = {k: type_map[v] for k, v in search_fields.items()}
        return cls.search_fields

    async def create_query(
        self,
        query: str,
        query_fields: str = None,
        default_field: Optional[str] = "patentTitle",
        facet: str = False,
        return_fields: Optional[List[str]] = None,
        filter_query: Optional[List[str]] = None,
        minimum_match: str = "100%",
        sort: Optional[str] = "applId asc",
        start: int = 0,
        rows: Optional[int] = None,
    ) -> PedsPage:
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
            query_fields = list(f for f in (await self.get_search_fields()).keys() if f in query)
        if query_fields is None:
            query_fields = list((await self.get_search_fields()).keys())

        params = {
            "df": default_field,
            "qf": " ".join(query_fields),
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
        print(json.dumps(params))
        response = await session.post(
            url,
            json=params,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return PedsPageSchema().load(response.json())
