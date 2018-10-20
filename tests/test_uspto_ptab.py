import pytest

from ip.uspto_ptab import PtabTrial, PtabDocument

class TestPtab:
    def test_can_get_case(self):
        case = PtabTrial.objects.get('IPR2016-00831')
        assert case.patent_owner_name == 'Silicon Genesis Corporation'
    
    def test_can_get_set_of_cases(self):
        cases = PtabTrial.objects.filter(patent_owner_name='Silicon Genesis Corporation').order_by('trial_number')
        assert cases.count() == 3
        assert list(cases.all())[0].trial_number == 'IPR2016-00831'
        assert len(list(cases)) == 3

    def test_can_get_case_documents(self):
        case = PtabTrial.objects.get('IPR2016-00832')
        assert case.documents.count() == 77
        assert case.documents.first().title == 'U.S. Provisional Application No. 60/046,276'
        assert case.documents.values_list('title', flat=True)[:5] == ['U.S. Provisional Application No. 60/046,276', 'U.S. Patent No. 5,374,564', 'L. Wegmann, Historical Perspective and Future Trends for Ion Implantation Systems (1981)', 'U.S. Patent No. 5,559,043', 'Prosecution History of U.S. Patent No. 6,013,563']
    
    def test_can_get_case_from_document(self):
        doc = PtabDocument.objects.get(230910)
        assert doc.trial.trial_number == 'IPR2016-00831'
    
    def test_can_download_document(self, tmpdir):
        doc = PtabDocument.objects.get(230910)
        doc.download(path=tmpdir)
        expected_doc = tmpdir / 'U.S. Provisional Application No. 60_046,276.pdf'
        assert expected_doc.exists()