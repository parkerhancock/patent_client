import typing as tp
from pathlib import Path

import lxml.etree as ET

from ..http_client import PatentClientAsyncHttpClient
from patent_client import function_cache

allowed_filters = [
    "PCTNumber",
    "OwnerName",
    "CorrespondentName",
    "PriorOwnerName",
    "ApplicationNumber",
    "PatentNumber",
    "PublicationNumber",
    "IntlRegistrationNumber",
    "ReelFrame",
]

allowed_sorts = ["ExecutionDate+desc", "ExecutionDate+asc"]


def validate_input(input, input_name, allowed_values):
    if input not in allowed_values:
        raise ValueError(f"{input_name} must be one of {allowed_values}")


class AssignmentApi:
    http_client = PatentClientAsyncHttpClient()

    @classmethod
    @function_cache
    async def lookup(cls, query: str, filter: str, rows=8, start=0, sort="ExecutionDate+desc") -> ET._Element:
        # Because of their limited utility, we omit fields, highlight, and facet
        url = "https://assignment-api.uspto.gov/patent/lookup"
        validate_input(filter, "filter", allowed_filters)
        validate_input(sort, "sort", allowed_sorts)
        response = await cls.http_client.get(
            url,
            params={
                "filter": filter,
                "query": query,
                "rows": rows,
                "start": start,
                "sort": sort,
                "facet": "false",
            },
            headers={"Accept": "application/xml"},
        )
        response.raise_for_status()
        return ET.fromstring(response.content)

    @classmethod
    async def download_pdf(cls, reel: str, frame: str, path: tp.Optional[Path] = None) -> Path:
        url = f"https://legacy-assignments.uspto.gov/assignments/assignment-pat-{reel}-{frame}.pdf"
        return await cls.http_client.download(url, "GET", path=path)