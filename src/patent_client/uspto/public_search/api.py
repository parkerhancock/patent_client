import asyncio
from pathlib import Path

import requests

from .session import aclient


class UsptoException(Exception):
    pass


def force_list(obj):
    if not isinstance(obj, list):
        return [
            obj,
        ]
    return obj


class PublicSearchAsyncApi:
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
    ):
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
        query_response = await aclient.post(url, json=data)
        if query_response.status_code in (500, 415):
            await asyncio.sleep(5)
            query_response = await aclient.post(url, json=data)
        query_response.raise_for_status()
        result = query_response.json()
        if result.get("error", None) is not None:
            raise UsptoException(f"Error #{result['error']['errorCode']}\n{result['error']['errorMessage']}")
        return result

    async def get_document(self, bib):
        url = f"https://ppubs.uspto.gov/dirsearch-public/patents/{bib.guid}/highlight"
        params = {
            "queryId": 1,
            "source": bib.type,
            "includeSections": True,
            "uniqueId": None,
        }
        response = await aclient.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_session(self):
        url = "https://ppubs.uspto.gov/dirsearch-public/users/me/session"
        response = await aclient.post(url, json=-1)  # json=str(random.randint(10000, 99999)))
        self.session = response.json()
        self.case_id = self.session["userCase"]["caseId"]
        return self.session

    async def _request_save(self, obj):
        page_keys = [f"{obj.image_location}/{i:0>8}.tif" for i in range(1, obj.document_structure.page_count + 1)]
        response = await aclient.post(
            "https://ppubs.uspto.gov/dirsearch-public/print/imageviewer",
            json={
                "caseId": self.case_id,
                "pageKeys": page_keys,
                "patentGuid": obj.guid,
                "saveOrPrint": "save",
                "source": obj.type,
            },
        )
        response.raise_for_status()
        return response.text

    async def download_image(self, obj, path="."):
        out_path = Path(path).expanduser() / f"{obj.guid}.pdf"
        if out_path.exists():
            return out_path
        if self.case_id is None:
            await self.get_session()
        try:
            print_job_id = await self._request_save(obj)
        except requests.exceptions.HTTPError:
            await self.get_session()
            print_job_id = await self._request_save(obj)
        while True:
            response = await aclient.post(
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
        async with aclient.stream("GET", f"https://ppubs.uspto.gov/dirsearch-public/print/save/{pdf_name}") as response:
            with out_path.open("wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return out_path
