import asyncio
import json
from copy import deepcopy
from pathlib import Path

import httpx

from patent_client._async.http_client import PatentClientSession

from .model import PublicSearchBiblioPage, PublicSearchDocument


class UsptoException(Exception):
    pass


def force_list(obj):
    if not isinstance(obj, list):
        return [
            obj,
        ]
    return obj


class PublicSearchApi:
    def __init__(self):
        self.client = PatentClientSession(
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Origin": "https://ppubs.uspto.gov",
                "Referer": "https://ppubs.uspto.gov/pubwebapp/",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Priority": "u=1, i",
            },
            http2=True,
            follow_redirects=True,
        )
        self.session = dict()
        self.case_id = None
        self.queries = dict()
        self.search_query = json.loads((Path(__file__).parent / "search_query.json").read_text())

    async def run_query(
        self,
        query,
        start=0,
        limit=500,
        sort="date_publ desc",
        default_operator="OR",
        sources=["US-PGPUB", "USPAT", "USOCR"],
        expand_plurals=True,
        british_equivalents=True,
    ) -> "PublicSearchBiblioPage":
        if self.case_id is None:
            await self.get_session()

        data = deepcopy(self.search_query)
        data["start"] = start
        data["pageCount"] = limit
        data["sort"] = sort
        data["query"]["caseId"] = self.case_id
        data["query"]["op"] = default_operator
        data["query"]["q"] = query
        data["query"]["queryName"] = query
        data["query"]["userEnteredQuery"] = query
        data["query"]["databaseFilters"] = [
            {"databaseName": s, "countryCodes": []} for s in sources
        ]
        data["query"]["plurals"] = expand_plurals
        data["query"]["britishEquivalents"] = british_equivalents

        counts = await self.make_request(
            "POST",
            "https://ppubs.uspto.gov/dirsearch-public/searches/counts",
            json=data["query"],
        )
        counts.raise_for_status()
        search_url = "https://ppubs.uspto.gov/dirsearch-public/searches/searchWithBeFamily"
        query_response = await self.make_request("POST", search_url, json=data)
        query_response.raise_for_status()
        result = query_response.json()
        if result.get("error", None) is not None:
            raise UsptoException(
                f"Error #{result['error']['errorCode']}\n{result['error']['errorMessage']}"
            )
        return PublicSearchBiblioPage.model_validate(result)

    async def make_request(self, method, url, **kwargs):
        response = await self.client.request(method, url, **kwargs)
        if response.status_code == 403:
            await self.get_session()
            response = await self.client.request(method, url, **kwargs)
        if response.status_code == 429:
            wait_time = int(response.headers["x-rate-limit-retry-after-seconds"]) + 1
            await asyncio.sleep(wait_time)
            response = await self.client.request(method, url, **kwargs)
        return response

    async def get_document(self, bib) -> "PublicSearchDocument":
        url = f"https://ppubs.uspto.gov/dirsearch-public/internal/patents/{bib.guid}/highlight"
        params = {
            "queryId": 1,
            "source": bib.type,
            "includeSections": True,
            "uniqueId": None,
        }
        response = await self.make_request("GET", url, params=params)
        response.raise_for_status()
        return PublicSearchDocument.model_validate(response.json())

    async def get_session(self):
        self.client.cookies = httpx.Cookies()
        response = await self.client.get("https://ppubs.uspto.gov/pubwebapp/")
        url = "https://ppubs.uspto.gov/dirsearch-public/users/me/session"
        response = await self.client.post(
            url,
            json=-1,
            headers={
                "X-Access-Token": "null",
                "referer": "https://ppubs.uspto.gov/pubwebapp/",
            },
        )  # json=str(random.randint(10000, 99999)))
        self.session = response.json()
        self.case_id = self.session["userCase"]["caseId"]
        self.access_token = response.headers["X-Access-Token"]
        self.client.headers["X-Access-Token"] = self.access_token
        return self.session

    async def _request_save(self, obj):
        page_keys = [
            f"{obj.image_location}/{i:0>8}.tif"
            for i in range(1, obj.document_structure.page_count + 1)
        ]
        response = await self.client.post(
            "https://ppubs.uspto.gov/dirsearch-public/internal/print/imageviewer",
            json={
                "caseId": self.case_id,
                "pageKeys": page_keys,
                "patentGuid": obj.guid,
                "saveOrPrint": "save",
                "source": obj.type,
            },
        )
        if response.status_code == 500:
            raise UsptoException(response.text)
        return response.text

    async def download_image(self, obj, path="."):
        out_path = Path(path).expanduser() / f"{obj.guid}.pdf"
        if out_path.exists():
            return out_path
        if self.case_id is None:
            await self.get_session()
        try:
            print_job_id = await self._request_save(obj)
        except httpx.HTTPStatusError:
            await self.get_session()
            print_job_id = await self._request_save(obj)
        while True:
            response = await self.client.post(
                "https://ppubs.uspto.gov/dirsearch-public/internal/print/print-process",
                json=[
                    print_job_id,
                ],
            )
            response.raise_for_status()
            print_data = response.json()
            if print_data[0]["printStatus"] == "COMPLETED":
                break
            await asyncio.sleep(1)
        pdf_name = print_data[0]["pdfName"]
        with out_path.open("wb") as f:
            try:
                request = self.client.build_request(
                    "GET",
                    f"https://ppubs.uspto.gov/dirsearch-public/internal/print/save/{pdf_name}",
                )
                response = await self.client.send(request, stream=True)
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    if chunk:
                        f.write(chunk)
            except httpx.HTTPStatusError as e:
                await response.aclose()
                raise e
        return out_path
