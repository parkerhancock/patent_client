import os

import pytest

from ..exceptions import FullTextNotAvailable
from ..exceptions import ThrottleException
from .model import Patent

HERE = os.path.dirname(__file__)


class TestPatentFullText:
    def test_fetch_patent(self):
        pat = Patent.objects.get(6095661)
        assert pat.title == "Method and apparatus for an L.E.D. flashlight"
        assert len(pat.abstract) == 1543

    def test_claims(self):
        pat_no = 6095661
        pat = Patent.objects.get(6095661)
        assert len(pat.parsed_claims) == 52
        assert pat.parsed_claims[0].number == 1
        assert len(pat.parsed_claims[0].text) == 1269
        assert len(pat.parsed_claims[0].limitations) == 5
        assert pat.parsed_claims[30].number == 31
        assert len(pat.parsed_claims[30].text) == 461
        assert len(pat.parsed_claims[30].limitations) == 4
        assert not pat.parsed_claims[30].dependent
        assert pat.parsed_claims[30].independent
        assert pat.parsed_claims[30].depends_on == list()
        assert pat.parsed_claims[31].dependent
        assert not pat.parsed_claims[31].independent
        assert pat.parsed_claims[31].depends_on == [
            31,
        ]

    def test_us8645300(self):
        pat_no = 8645300
        pat = Patent.objects.get(pat_no)
        assert pat.title == "System and method for intent data processing"

    def test_search_classification(self):
        query = "CCL/166/308.1 AND APD/19000101->20121005"
        results = Patent.objects.filter(query=query)
        assert len(results) >= 829
        assert results[50].publication_number == "8874376"
        assert len(list(results[:15])) == 15

    def test_can_fetch_reissue_applications(self):
        pat_no = "RE43633"
        pat = Patent.objects.get(pat_no)
        assert pat.title == "System and method for linking streams of multimedia data to reference material for display"
        assert pat.parsed_claims[0].text[:25] == "1. .[.A system for linkin"

    def test_can_get_field_of_search(self):
        pat_no = "9140110"
        pat = Patent.objects.get(pat_no)
        assert len(pat.field_of_search) == 6
        pat_no = "8832265"
        pat = Patent.objects.get(pat_no)
        assert len(pat.field_of_search) == 7

    @pytest.mark.skip("Unknown if we need to keep this exception")
    def test_shows_error_for_old_patents(self):
        pat_no = "3,113,620"
        with pytest.raises(FullTextNotAvailable) as exception:
            pat = Patent.objects.get(pat_no)

    @pytest.mark.skip("Needs More Work")
    def test_handles_being_throttled(self):
        pat = Patent.objects.get("1111111")
        pat._html_page = open(os.path.join(HERE, "fixtures", "error.html"), "r").read()
        with pytest.raises(ThrottleException) as e:
            title = pat.title

    def test_handles_missing_app_id(self):
        """Some 1990's patents don't have an application ID on their FT page"""
        num = "5890536"
        pat = Patent.objects.get(num)
        assert pat.appl_id == None

    def test_handles_disclaimers(self):
        """Some patents have notice markers on the issue date regarding statutory disclaimers"""
        pat = Patent.objects.get("5439055")
        assert pat.publication_date.isoformat() == "1995-08-08"

    def test_handles_claims_for_US6460631(self):
        pat = Patent.objects.get(6460631)
        for claim in pat.parsed_claims:
            pass
        assert True

    def test_handles_search_without_results(self):
        query = Patent.objects.filter(query="CCL/379/56 AND APD/19700101->19950928")
        assert len(query) == 0

    def test_can_get_forward_references(self):
        pat = Patent.objects.get(6103599)
        forward_refs = pat.forward_citations
        assert len(forward_refs) >= 134

    def test_splits_claims_properly(self):
        pat = Patent.objects.get(9945180)
        claim1 = pat.parsed_claims[0]
        print(repr(claim1.text))
        test_claim_1 = """1. A ground drilling machine comprising:
a rack including an up hole end and a down hole end;
a rod drive unit movably mounted on the rack, the rod drive unit configured to thread a drill rod to a drill string;
a rod loader arm configured to move a drill rod from a rod box into alignment with the rod drive unit and secure the drill rod as it is threaded to the drive unit;
a vise assembly connected to the rack at a down hole end, the vise assembly including a lower vise that is configured when activated to support the weight of a drill string and prevent rotation of the drill string; and
a control system is configured to automatically deactivate a user control vise release to prevent release of the lower vise until the rod drive unit applies a predetermined level of torque to the drill rod; and
wherein the control system is configured to determine whether the predetermined level of torque is applied based on applying a certain level of torque to the drill rod by the drive unit for a set time interval."""
        print(repr(claim1.text))
        assert claim1.text == test_claim_1
        assert len(claim1.limitations) == 7
        assert (
            claim1.limitations[-2]
            == "a control system is configured to automatically deactivate a user control vise release to prevent release of the lower vise until the rod drive unit applies a predetermined level of torque to the drill rod; and"
        )
        assert (
            claim1.limitations[-1]
            == "wherein the control system is configured to determine whether the predetermined level of torque is applied based on applying a certain level of torque to the drill rod by the drive unit for a set time interval."
        )
        assert claim1.limitations[-1].split()[0] == "wherein"

    def test_classifications_with_foreign_priority_data(self):
        pat = Patent.objects.get(7752445)
        assert len(pat.us_classes) == 6
        assert pat.foreign_priority[0].number == "2004-052835"

    def test_can_get_design_patents(self):
        pat = Patent.objects.get("D645062")
        assert pat.title == "Gripping arm"
        assert pat.appl_id == "29380046"

    def test_search_that_has_single_patent(self):
        result = Patent.objects.filter(title="tennis", issue_date="2010-01-01->2010-02-27")
        assert len(result) == 1
        obj = result.first()
        assert obj.seq == 1
        assert obj.publication_number == "7658211"
        assert obj.title == "Tennis ball recharging apparatus method"