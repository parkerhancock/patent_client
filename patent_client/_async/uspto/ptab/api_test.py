import pytest

from .api import PtabApi


class TestPtabApi:
    @pytest.mark.asyncio
    async def test_can_get_document(self):
        page = await PtabApi.get_documents(document_identifier="170680401")
        assert len(page.docs) == 1

    @pytest.mark.asyncio
    async def test_can_get_document_range(self):
        page = await PtabApi.get_documents(
            proceeding_number="IPR2022-00037",
            document_filing_date=("2023-01-01", "2023-09-15"),
        )
        assert len(page.docs) == 25

    @pytest.mark.asyncio
    async def test_can_get_proceeding(self):
        page = await PtabApi.get_proceedings(proceeding_number="IPR2022-00037")
        assert len(page.docs) == 1
