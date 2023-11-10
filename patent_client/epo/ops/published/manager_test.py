import pytest

from . import api
from ..session import asession
from ..session import OpsAsyncSession
from ..session import OpsAuthenticationError
from .model.search import Inpadoc
from patent_client.util.hishel_util import cache_disabled


class TestPublished:
    def test_inpadoc_manager(self):
        result = Inpadoc.objects.filter(applicant="Microsoft")
        assert len(result) > 20
        countries = list(result.limit(20).values_list("country", flat=True))
        assert sum(1 for c in countries if c == "US") >= 1

    def test_get_biblio_from_result(self):
        doc = Inpadoc.objects.filter(applicant="Google").first()
        result = doc.biblio
        assert result.title is not None

    def test_get_claims_from_result(self):
        result = Inpadoc.objects.get("WO2009085664A2")
        assert len(result.claims.claims) == 20
        assert len(result.claims.claim_text) == 4830

    def test_get_description_from_result(self):
        result = Inpadoc.objects.get("WO2009085664A2")
        assert len(result.description) == 47955

    def test_get_family_from_result(self):
        result = Inpadoc.objects.get("WO2009085664A2")
        assert len(result.family) >= 20

    def test_get_biblio_from_wo(self):
        result = Inpadoc.objects.get("WO2009085664A2").biblio
        assert result.abstract is not None

    def test_can_index_inpadoc_result(self):
        result = Inpadoc.objects.filter(applicant="Tesla")
        first_obj = result[0]
        second_obj = result[1]
        assert first_obj != second_obj

    def test_can_handle_single_item_ipc_classes(self):
        result = Inpadoc.objects.get("WO2020081771").biblio
        assert result.intl_class is not None

    def test_issue_41(self):
        result = Inpadoc.objects.get("JP2005533465A").biblio
        assert result.title == None

    def test_issue_76_no_credential(self):
        good_session = api.asession
        api.asession = OpsAsyncSession()
        with cache_disabled(asession):
            with pytest.raises(OpsAuthenticationError):
                pub = Inpadoc.objects.get("EP3082535A1")
        api.asession = good_session

    def test_issue_76_with_credential(self):
        pub = Inpadoc.objects.get("EP3082535A1")
        assert pub.biblio.title == "AUTOMATIC FLUID DISPENSER"


class TestPublishedAsync:
    @pytest.mark.asyncio
    async def test_inpadoc_manager(self):
        result = Inpadoc.objects.filter(applicant="Microsoft")
        assert await result.alen() > 20
        countries = await result.limit(20).values_list("country", flat=True).ato_list()
        assert sum(1 for c in countries if c == "US") >= 1

    @pytest.mark.asyncio
    async def test_get_biblio_from_result(self):
        doc = await Inpadoc.objects.filter(applicant="Google").afirst()
        result = doc.biblio
        assert result.title is not None

    @pytest.mark.asyncio
    async def test_get_claims_from_result(self):
        result = await Inpadoc.objects.aget("WO2009085664A2")
        assert len(result.claims.claims) == 20
        assert len(result.claims.claim_text) == 4830

    @pytest.mark.asyncio
    async def test_get_description_from_result(self):
        result = await Inpadoc.objects.aget("WO2009085664A2")
        assert len(result.description) == 47955

    @pytest.mark.asyncio
    async def test_get_family_from_result(self):
        result = await Inpadoc.objects.aget("WO2009085664A2")
        assert len(result.family) >= 20

    @pytest.mark.asyncio
    async def test_get_biblio_from_wo(self):
        result = await Inpadoc.objects.aget("WO2009085664A2")
        assert result.biblio.abstract is not None

    @pytest.mark.asyncio
    async def test_can_index_inpadoc_result(self):
        result = Inpadoc.objects.filter(applicant="Tesla")
        first = await result.afirst()
        second = await result.offset(1).afirst()
        assert first != second

    @pytest.mark.asyncio
    async def test_can_handle_single_item_ipc_classes(self):
        result = await Inpadoc.objects.aget("WO2020081771")
        assert result.biblio.intl_class is not None

    @pytest.mark.asyncio
    async def test_issue_41(self):
        result = await Inpadoc.objects.aget("JP2005533465A")
        assert result.biblio.title == None

    @pytest.mark.asyncio
    async def test_issue_76_with_credential(self):
        pub = await Inpadoc.objects.aget("EP3082535A1")
        assert pub.biblio.title == "AUTOMATIC FLUID DISPENSER"
