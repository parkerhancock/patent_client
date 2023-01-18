import pytest

from ..session import OpsAuthenticationError
from ..session import session
from .model.search import Inpadoc


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
        assert result[0] != result[1]

    def test_can_handle_single_item_ipc_classes(self):
        result = Inpadoc.objects.get("WO2020081771").biblio
        assert result.intl_class is not None

    def test_issue_41(self):
        result = Inpadoc.objects.get("JP2005533465A").biblio
        assert result.title == None

    def test_issue_76_no_credential(self):
        key = session.key
        session.key = None
        with pytest.raises(OpsAuthenticationError):
            pub = Inpadoc.objects.get("EP3082535A1")
        session.key = key

    def test_issue_76_with_credential(self):
        pub = Inpadoc.objects.get("EP3082535A1")
        assert pub.biblio.title == "AUTOMATIC FLUID DISPENSER"
