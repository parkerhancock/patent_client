import pytest
from . import PtabProceeding, PtabDocument, PtabDecision

class TestPtabProceeding:
    def test_get_by_proceeding_number(self):
        result = PtabProceeding.objects.get("IPR2016-00831")
        assert result.respondent_patent_number == "6162705"

    def test_filter_by_party(self):
        result = PtabProceeding.objects.filter(party_name="Apple")
        assert len(result) >= 444
        assert result.count() >= 444

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
        assert len(result) == 78

    def test_sort_by_document_number(self):
        result = (
            PtabDocument.objects.filter(proceeding_number="IPR2016-00831")
            .order_by("document_number")
            .limit(3)
            .values_list("document_number", flat=True)
        )
        assert len(result) == 3
        objects = list(result)
        assert objects == list(sorted(objects))

class TestPtabDecision:
    def test_get_by_proceeding(self):
        result = PtabDecision.objects.get(proceeding_number="IPR2016-00831")
        assert (
            result.identifier
            == "a44c5f1557b7b60d00e66604d3668ce442d53f964aa597011cc476b4"
        )