import typing as tp
from pathlib import Path

import anyio
import httpx

from ..http_client import PatentClientAsyncHttpClient
from patent_client import function_cache


class UsptoException(Exception):
    pass


def force_list(obj: tp.Union[str, tp.Sequence[str]]) -> list[str]:
    if isinstance(obj, str):
        return [
            obj,
        ]
    elif isinstance(obj, tp.Sequence):
        return list(obj)
    return obj


class PublicSearchApi:
    http_client = PatentClientAsyncHttpClient(
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Referer": "https://ppubs.uspto.gov/pubwebapp/",
        },
        http2=True,
    )
    session = dict()
    case_id = None

    @classmethod
    def prepare_query_params(
        cls,
        query: str,
        start: int,
        limit: int,
        sort: str,
        default_operator: str,
        sources: tuple[str],
        expand_plurals: bool,
        british_equivalents: bool,
    ) -> tp.Any:
        data = {
            "start": start,
            "pageCount": limit,
            "sort": sort,
            "docFamilyFiltering": "familyIdFiltering",
            "searchType": 1,
            "familyIdEnglishOnly": True,
            "familyIdFirstPreferred": "US-PGPUB",
            "familyIdSecondPreferred": "USPAT",
            "familyIdThirdPreferred": "FPRS",
            "showDocPerFamilyPref": "showEnglish",
            "queryId": 0,
            "tagDocSearch": False,
            "query": {
                "caseId": cls.case_id,
                "hl_snippets": "2",
                "op": default_operator,
                "q": query,
                "queryName": query,
                "highlights": "1",
                "qt": "brs",
                "spellCheck": False,
                "viewName": "tile",
                "plurals": expand_plurals,
                "britishEquivalents": british_equivalents,
                "searchType": 1,
                "ignorePersist": True,
                "userEnteredQuery": query,
            },
        }
        database_filters = [{"databaseName": s, "countryCodes": []} for s in force_list(sources)]
        data["query"]["databaseFilters"] = database_filters
        return data

    @classmethod
    @function_cache
    async def query(
        cls,
        query: str,
        start: int = 0,
        limit: int = 500,
        sort: str = "date_publ desc",
        default_operator: str = "OR",
        sources: tuple[str] = ("US-PGPUB", "USPAT", "USOCR"),
        expand_plurals: bool = True,
        british_equivalents: bool = True,
    ) -> tp.Any:
        if cls.case_id is None:
            await cls._get_session()
        url = r"https://ppubs.uspto.gov/dirsearch-public/searches/searchWithBeFamily"
        data = cls.prepare_query_params(
            query, start, limit, sort, default_operator, sources, expand_plurals, british_equivalents
        )
        query_response = await cls.http_client.post(url, json=data)
        if query_response.status_code in (500, 415):  # Just need to retry
            await anyio.sleep(5)
            query_response = await cls.http_client.post(url, json=data)
        elif query_response.status_code in (400, 403):  # Session must be refreshed
            await cls._get_session()
            data = cls.prepare_query_params(
                query, start, limit, sort, default_operator, sources, expand_plurals, british_equivalents
            )
            query_response = await cls.http_client.post(url, json=data)
        query_response.raise_for_status()
        result = query_response.json()
        if result.get("error", None) is not None:
            raise UsptoException(f"Error #{result['error']['errorCode']}\n{result['error']['errorMessage']}")
        return result

    @classmethod
    @function_cache
    async def get_document(cls, guid: str, source: str) -> tp.Any:
        url = f"https://ppubs.uspto.gov/dirsearch-public/patents/{guid}/highlight"
        params = {
            "queryId": 1,
            "source": source,
            "includeSections": True,
            "uniqueId": None,
        }
        response = await cls.http_client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @classmethod
    async def _get_session(cls) -> None:
        url = "https://ppubs.uspto.gov/dirsearch-public/users/me/session"
        response = await cls.http_client.post(url, json=-1)  # json=str(random.randint(10000, 99999)))
        cls.session = response.json()
        cls.case_id = cls.session["userCase"]["caseId"]

    @classmethod
    async def _request_save(self, guid, image_location, source, page_count) -> str:
        page_keys = [f"{image_location}/{i:0>8}.tif" for i in range(1, page_count + 1)]
        response = await self.http_client.post(
            "https://ppubs.uspto.gov/dirsearch-public/print/imageviewer",
            json={
                "caseId": self.case_id,
                "pageKeys": page_keys,
                "patentGuid": guid,
                "saveOrPrint": "save",
                "source": source,
            },
        )
        if response.status_code == 500:
            raise UsptoException(response.text)
        return response.text

    @classmethod
    @function_cache
    async def download_images(
        cls, guid: str, image_location: str, source: str, page_count: int, path: tp.Optional[tp.Union[str, Path]] = None
    ) -> Path:
        path = Path(path) if path is not None else Path.cwd()
        if path.is_dir():
            path = path / f"{guid}.pdf"
        if path.exists():
            return path
        if cls.case_id is None:
            await cls._get_session()
        try:
            print_job_id = await cls._request_save(guid, image_location, source, page_count)
        except httpx.HTTPStatusError:
            await cls.get_session()
            print_job_id = await cls._request_save(guid, image_location, source, page_count)
        while True:
            response = await cls.http_client.post(
                "https://ppubs.uspto.gov/dirsearch-public/print/print-process",
                json=[
                    print_job_id,
                ],
            )
            response.raise_for_status()
            print_data = response.json()
            if print_data[0]["printStatus"] == "COMPLETED":
                break
            await anyio.sleep(1)
        pdf_name = print_data[0]["pdfName"]
        return await cls.http_client.download(
            f"https://ppubs.uspto.gov/dirsearch-public/print/save/{pdf_name}",
            method="GET",
            path=path,
        )
