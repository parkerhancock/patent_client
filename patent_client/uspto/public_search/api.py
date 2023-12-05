import asyncio
from pathlib import Path

import httpx

from .model import PublicSearchBiblioPage
from .model import PublicSearchDocument
from .session import session


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
        self.session = dict()
        self.case_id = None

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
    ) -> "PublicSearch":
        if self.case_id is None:
            await self.get_session()
        url = "https://ppubs.uspto.gov/dirsearch-public/searches/searchWithBeFamily"
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
                "caseId": self.case_id,
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
                "databaseFilters": [],
                "searchType": 1,
                "ignorePersist": True,
                "userEnteredQuery": query,
            },
        }
        for s in force_list(sources):
            data["query"]["databaseFilters"].append({"databaseName": s, "countryCodes": []})
        query_response = await session.post(url, json=data)
        if query_response.status_code in (500, 415):
            await asyncio.sleep(5)
            query_response = await session.post(url, json=data)
        elif query_response.status_code == 403:
            await self.get_session()
            query_response = await session.post(url, json=data)
        query_response.raise_for_status()
        result = query_response.json()
        if result.get("error", None) is not None:
            raise UsptoException(f"Error #{result['error']['errorCode']}\n{result['error']['errorMessage']}")
        return PublicSearchBiblioPage.model_validate(result)

    async def get_document(self, bib) -> "PublicSearchDocument":
        url = f"https://ppubs.uspto.gov/dirsearch-public/patents/{bib.guid}/highlight"
        params = {
            "queryId": 1,
            "source": bib.type,
            "includeSections": True,
            "uniqueId": None,
        }
        response = await session.get(url, params=params)
        response.raise_for_status()
        return PublicSearchDocument.model_validate(response.json())

    async def get_session(self):
        url = "https://ppubs.uspto.gov/dirsearch-public/users/me/session"
        response = await session.post(
            url, json=-1, extensions={"cache_disabled": True}
        )  # json=str(random.randint(10000, 99999)))
        self.session = response.json()
        self.case_id = self.session["userCase"]["caseId"]
        return self.session

    async def _request_save(self, obj):
        page_keys = [f"{obj.image_location}/{i:0>8}.tif" for i in range(1, obj.document_structure.page_count + 1)]
        response = await session.post(
            "https://ppubs.uspto.gov/dirsearch-public/print/imageviewer",
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
            response = await session.post(
                "https://ppubs.uspto.gov/dirsearch-public/print/print-process",
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
                request = session.build_request(
                    "GET", f"https://ppubs.uspto.gov/dirsearch-public/print/save/{pdf_name}"
                )
                response = await session.send(request, stream=True)
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    if chunk:
                        f.write(chunk)
            except httpx.HTTPStatusError as e:
                await response.aclose()
                raise e
        return out_path
