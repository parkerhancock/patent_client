import pytest

from .api import OfficeActionApi


class TestOfficeActionApi:
    @pytest.mark.asyncio
    async def test_get_rejection_fields(self):
        data = await OfficeActionApi.get_rejection_fields()
        assert data["apiKey"] == "oa_rejections"
        assert data["fieldCount"] == 34

    @pytest.mark.asyncio
    async def test_get_citation_fields(self):
        data = await OfficeActionApi.get_citation_fields()
        assert data["apiKey"] == "oa_citations"
        assert data["fieldCount"] == 16

    @pytest.mark.asyncio
    async def test_get_fulltext_fields(self):
        data = await OfficeActionApi.get_fulltext_fields()
        assert data["apiKey"] == "oa_actions"
        assert data["fieldCount"] == 133
