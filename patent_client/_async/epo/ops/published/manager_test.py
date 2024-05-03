import pytest

from .model.search import Inpadoc


class TestPublished:
    @pytest.mark.asyncio
    async def test_inpadoc_manager(self):
        result = Inpadoc.objects.filter(applicant="Microsoft")
        assert await result.count() > 20
        countries = [c async for c in result.limit(20).values_list("country", flat=True)]
        assert sum(1 for c in countries if c == "US") >= 1

    @pytest.mark.asyncio
    async def test_get_biblio_from_result(self):
        doc = await Inpadoc.objects.filter(applicant="Google").first()
        result = await doc.biblio
        assert len(result.titles) > 0

    @pytest.mark.asyncio
    async def test_get_claims_from_result(self):
        result = await Inpadoc.objects.get("WO2009085664A2")
        claims = await result.claims
        assert len(claims.claims) == 20
        assert len(claims.claim_text) == 4830

    @pytest.mark.asyncio
    async def test_get_description_from_result(self):
        result = await Inpadoc.objects.get("WO2009085664A2")
        description = await result.description
        assert len(description) == 47955

    @pytest.mark.asyncio
    async def test_get_family_from_result(self):
        result = await Inpadoc.objects.get("WO2009085664A2")
        family = await result.family
        assert len(family) >= 20

    @pytest.mark.asyncio
    async def test_get_biblio_from_wo(self):
        result = await Inpadoc.objects.get("WO2009085664A2")
        biblio = await result.biblio
        assert biblio.abstract is not None

    @pytest.mark.asyncio
    async def test_can_index_inpadoc_result(self):
        result = Inpadoc.objects.filter(applicant="Tesla")
        first = await result.first()
        second = await result.offset(1).first()
        assert first != second

    @pytest.mark.asyncio
    async def test_can_handle_single_item_ipc_classes(self):
        result = await Inpadoc.objects.get("WO2020081771")
        biblio = await result.biblio
        assert biblio.intl_class is not None

    @pytest.mark.asyncio
    async def test_issue_41(self):
        result = await Inpadoc.objects.get("JP2005533465A")
        biblio = await result.biblio
        assert biblio.title is None

    @pytest.mark.asyncio
    async def test_document_downloading(self, tmpdir):
        result = await Inpadoc.objects.get("WO2010050748A2")
        await result.download(tmpdir)
        assert len(tmpdir.listdir()) > 0
