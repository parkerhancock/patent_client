import pytest

from .model import PtabDecision
from .model import PtabDocument
from .model import PtabProceeding


class TestPtabProceeding:
    def test_get_by_proceeding_number(self):
        result = PtabProceeding.objects.get("IPR2016-00831")
        assert result.respondent_patent_number == "6162705"

    def test_get_by_patent_number(self):
        result = PtabProceeding.objects.get(patent_number="6103599")
        assert result.proceeding_number == "IPR2016-00833"

    def test_get_by_application_number(self):
        result = PtabProceeding.objects.get(appl_id="09089931")
        assert result.proceeding_number == "IPR2016-00833"

    def test_filter_by_party(self):
        result = PtabProceeding.objects.filter(party_name="Apple")
        assert len(result) >= 400
        assert result.count() >= 400

    def test_filter_with_limit(self):
        result = PtabProceeding.objects.filter(party_name="Apple").limit(26)
        assert len(result) == 26
        objects = list(result)
        assert len(objects) == 26

    def test_offset(self):
        result = PtabProceeding.objects.filter(party_name="Apple").limit(3)
        objects = list(result)
        assert result.first() == objects[0]
        assert result.offset(1).first() == objects[1]
        assert result.offset(1).offset(1).first() == objects[2]


class TestPtabDocument:
    def test_filter_by_proceeding(self):
        result = PtabDocument.objects.filter(proceeding_number="IPR2016-00831")
        assert len(result) == 77

    def test_sort_by_document_number(self):
        result = (
            PtabDocument.objects.filter(proceeding_number="IPR2016-00831")
            .order_by("document_number")
            .limit(3)
            .values_list("document_number", flat=True)
            .to_list()
        )
        assert len(result) == 3
        objects = list(result)
        assert objects == list(sorted(objects))


class TestPtabDecision:
    def test_get_by_proceeding(self):
        result = PtabDecision.objects.get(proceeding_number="IPR2016-00831")
        assert result.identifier == "a44c5f1557b7b60d00e66604d3668ce442d53f964aa597011cc476b4"


class TestPtabProceedingAsync:
    @pytest.mark.asyncio
    async def test_get_by_proceeding_number(self):
        result = await PtabProceeding.objects.aget("IPR2016-00831")
        assert result.respondent_patent_number == "6162705"

    @pytest.mark.asyncio
    async def test_get_by_patent_number(self):
        result = await PtabProceeding.objects.aget(patent_number="6103599")
        assert result.proceeding_number == "IPR2016-00833"

    @pytest.mark.asyncio
    async def test_get_by_application_number(self):
        result = await PtabProceeding.objects.aget(appl_id="09089931")
        assert result.proceeding_number == "IPR2016-00833"

    @pytest.mark.asyncio
    async def test_filter_by_party(self):
        result = PtabProceeding.objects.filter(party_name="Apple")
        assert await result.alen() >= 400

    @pytest.mark.asyncio
    async def test_filter_with_limit(self):
        result = PtabProceeding.objects.filter(party_name="Apple").limit(26)
        assert await result.alen() == 26
        objects = await result.ato_list()
        assert len(objects) == 26

    @pytest.mark.asyncio
    async def test_offset(self):
        result = PtabProceeding.objects.filter(party_name="Apple").limit(3)
        objects = await result.ato_list()
        assert await result.afirst() == objects[0]
        assert await result.offset(1).afirst() == objects[1]
        assert await result.offset(1).offset(1).afirst() == objects[2]


class TestPtabDocument:
    @pytest.mark.asyncio
    async def test_filter_by_proceeding(self):
        result = PtabDocument.objects.filter(proceeding_number="IPR2016-00831")
        assert await result.alen() == 77

    @pytest.mark.asyncio
    async def test_sort_by_document_number(self):
        result = await (
            PtabDocument.objects.filter(proceeding_number="IPR2016-00831")
            .order_by("document_number")
            .limit(3)
            .values_list("document_number", flat=True)
            .ato_list()
        )
        assert len(result) == 3


class TestPtabDecision:
    @pytest.mark.asyncio
    async def test_get_by_proceeding(self):
        result = await PtabDecision.objects.aget(proceeding_number="IPR2016-00831")
        assert result.identifier == "a44c5f1557b7b60d00e66604d3668ce442d53f964aa597011cc476b4"
