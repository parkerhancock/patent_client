import pytest

from .model import PtabDecision, PtabDocument, PtabProceeding


class TestPtabProceeding:
    @pytest.mark.asyncio
    async def test_get_by_proceeding_number(self):
        result = await PtabProceeding.objects.get("IPR2016-00831")
        assert result.respondent_patent_number == "6162705"

    @pytest.mark.asyncio
    async def test_get_by_patent_number(self):
        result = await PtabProceeding.objects.get(patent_number="6103599")
        assert result.proceeding_number == "IPR2016-00833"

    @pytest.mark.asyncio
    async def test_get_by_application_number(self):
        result = await PtabProceeding.objects.get(appl_id="09089931")
        assert result.proceeding_number == "IPR2016-00833"

    @pytest.mark.asyncio
    async def test_filter_by_party(self):
        result = PtabProceeding.objects.filter(party_name="Apple")
        assert await result.count() >= 400

    @pytest.mark.asyncio
    async def test_filter_with_limit(self):
        result = PtabProceeding.objects.filter(party_name="Apple").limit(26)
        assert await result.count() == 26
        objects = [a async for a in result]
        assert len(objects) == 26

    @pytest.mark.asyncio
    async def test_offset(self):
        result = PtabProceeding.objects.filter(party_name="Apple").limit(3)
        objects = [a async for a in result]
        assert await result.first() == objects[0]
        assert await result.offset(1).first() == objects[1]
        assert await result.offset(1).offset(1).first() == objects[2]


class TestPtabDocument:
    @pytest.mark.asyncio
    async def test_filter_by_proceeding(self):
        result = PtabDocument.objects.filter(proceeding_number="IPR2016-00831")
        assert await result.count() == 77

    @pytest.mark.asyncio
    async def test_sort_by_document_number(self):
        result = (
            await PtabDocument.objects.filter(proceeding_number="IPR2016-00831").limit(3).count()
        )
        assert result == 3


class TestPtabDecision:
    @pytest.mark.asyncio
    async def test_get_by_proceeding(self):
        result = await PtabDecision.objects.get(proceeding_number="IPR2016-00831")
        assert result.identifier == "a44c5f1557b7b60d00e66604d3668ce442d53f964aa597011cc476b4"
