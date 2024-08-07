# ********************************************************************************
# *         WARNING: This file is automatically generated by unasync.py.         *
# *                             DO NOT MANUALLY EDIT                             *
# *         Source File: patent_client/_async/uspto/ptab/manager_test.py         *
# ********************************************************************************


from .model import PtabDecision, PtabDocument, PtabProceeding


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
        assert result.count() >= 400

    def test_filter_with_limit(self):
        result = PtabProceeding.objects.filter(party_name="Apple").limit(26)
        assert result.count() == 26
        objects = [a for a in result]
        assert len(objects) == 26

    def test_offset(self):
        result = PtabProceeding.objects.filter(party_name="Apple").limit(3)
        objects = [a for a in result]
        assert result.first() == objects[0]
        assert result.offset(1).first() == objects[1]
        assert result.offset(1).offset(1).first() == objects[2]


class TestPtabDocument:
    def test_filter_by_proceeding(self):
        result = PtabDocument.objects.filter(proceeding_number="IPR2016-00831")
        assert result.count() == 77
        assert (result.first()).document_title == "DECISION - Motion to Terminate"

    def test_sort_by_document_number(self):
        result = PtabDocument.objects.filter(proceeding_number="IPR2016-00831").limit(3).count()
        assert result == 3


class TestPtabDecision:
    def test_get_by_proceeding(self):
        result = PtabDecision.objects.get(proceeding_number="IPR2016-00831")
        assert result.identifier == "a44c5f1557b7b60d00e66604d3668ce442d53f964aa597011cc476b4"
