from pprint import pprint
from patent_client.epo.inpadoc.model import Inpadoc, InpadocBiblio


class TestInpadoc():
    def test_inpadoc_manager(self):
        result = Inpadoc.objects.filter(applicant="Microsoft")
        assert len(result) > 20
        countries = list(result.limit(20).values_list('country', flat=True))
        assert sum(1 for c in countries if c == 'US') >= 1
       
    def test_get_biblio_from_result(self):
        result = Inpadoc.objects.filter(applicant="Google").first().biblio
        assert result.title is not None

    def test_get_claims_from_result(self):
        result = Inpadoc.objects.get(publication="WO2009085664A2")
        assert len(result.claims) == 4833

    def test_get_description_from_result(self):
        result = Inpadoc.objects.get(publication="WO2009085664A2")
        assert len(result.description) == 47956

    def test_get_family_from_result(self):
        result = Inpadoc.objects.get(publication="WO2009085664A2")
        assert len(result.family) >= 20

    def test_get_biblio_from_wo(self):
        result = Inpadoc.objects.get(publication="WO2009085664A2").biblio
        breakpoint()
        assert result == True


    def test_can_index_inpadoc_result(self):
        result = Inpadoc.objects.filter(applicant='Tesla')
        assert result[0] != result[1]


class TestInpadocBiblio():
    def test_inpadoc_biblio_manager(self):
        result = InpadocBiblio.objects.get(publication="USD870008")
        assert result.title == "Vehicle side skirt"
        assert result.number == 'D870008'
        assert result.country == 'US'


class TestInpadocLinks():
    def test_get_us_application_from_result(self):
        result = Inpadoc.objects.get(publication="US8131731B2")
        assert result.us_application.patent_title == "RELEVANCY SORTING OF USER'S BROWSER HISTORY"
