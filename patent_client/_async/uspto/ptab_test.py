import pytest

from .ptab import PtabApi


@pytest.mark.asyncio
async def test_can_get_document():
    page = await PtabApi.get_documents(document_identifier="170680401")
    assert len(page["results"]) == 1


@pytest.mark.asyncio
async def test_can_get_document_range():
    page = await PtabApi.get_documents(
        proceeding_number="IPR2022-00037",
        document_filing_date=("2023-01-01", "2023-09-15"),
    )
    assert len(page["results"]) == 25


@pytest.mark.asyncio
async def test_can_get_proceeding():
    page = await PtabApi.get_proceedings(proceeding_number="IPR2022-00037")
    assert len(page["results"]) == 1
