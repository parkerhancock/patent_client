from .model import OfficeActionCitation
from .model import OfficeActionFullText
from .model import OfficeActionRejection


class TestOfficeActionRejection:
    def test_empty_query(self):
        obj = OfficeActionRejection.objects.first()
        assert obj.id == "40ae4cb8be9f1d54a7ecde0949468dc2"
        assert obj.appl_id == "14146331"

    def test_app_query(self):
        obj = OfficeActionRejection.objects.filter(appl_id="14574014").first()
        assert obj.appl_id == "14574014"


class TestOfficeActionCitation:
    def test_empty_query(self):
        obj = OfficeActionCitation.objects.first()
        assert obj.id == "75e94a544ff8f9aeb49581d9a9ec423a"
        assert obj.appl_id == "15539899"

    def test_app_query(self):
        obj = OfficeActionCitation.objects.filter(appl_id="14574014").first()
        assert obj.appl_id == "14574014"


class TestOfficeActionFullText:
    def test_empty_query(self):
        obj = OfficeActionFullText.objects.first()
        assert obj.id == "019e4cdece9a488ab845f8832409475845b90937fe3c8670125d0e61"
        assert obj.appl_id == "13088453"

    def test_app_query(self):
        obj = OfficeActionFullText.objects.filter(appl_id="14574014").first()
        assert obj.appl_id == "14574014"
