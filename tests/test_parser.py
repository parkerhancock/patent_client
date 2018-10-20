import pytest

from ip.parser import parse


class TestPatentNumberParser:
    def test_can_handle_integer_values(self):
        pat = parse(6013599)
        assert pat.number == "6013599"
        assert pat.country == "US"
        assert pat.kind_code == "B2"
        assert pat.display() == "US 6,013,599 B2"
        assert str(pat) == "US6013599B2"

        app = parse(20150012345)
        assert app.number == "20150012345"
        assert app.country == "US"
        assert app.kind_code == "A1"
        assert app.display() == "US 2015/0012345 A1"
        assert str(app) == "US20150012345A1"

    def test_can_handle_string_values_without_country_codes(self):
        pat = parse("6013599")
        assert pat.number == "6013599"
        assert pat.country == "US"
        assert pat.kind_code == "B2"
        assert pat.display() == "US 6,013,599 B2"
        assert str(pat) == "US6013599B2"

        app = parse("20150012345")
        assert app.number == "20150012345"
        assert app.country == "US"
        assert app.kind_code == "A1"
        assert app.display() == "US 2015/0012345 A1"
        assert str(app) == "US20150012345A1"

    def test_can_handle_us_without_kind_codes(self):
        pat = parse("US6013599")
        assert pat.number == "6013599"
        assert pat.country == "US"
        assert pat.kind_code == "B2"
        assert pat.display() == "US 6,013,599 B2"
        assert str(pat) == "US6013599B2"

        app = parse("US20150012345")
        assert app.number == "20150012345"
        assert app.country == "US"
        assert app.kind_code == "A1"
        assert app.display() == "US 2015/0012345 A1"
        assert str(app) == "US20150012345A1"

    def test_can_handle_us_with_kind_codes(self):
        pat = parse("US6013599B2")
        assert pat.number == "6013599"
        assert pat.country == "US"
        assert pat.kind_code == "B2"
        assert pat.display() == "US 6,013,599 B2"
        assert str(pat) == "US6013599B2"

        app = parse("US20150012345A1")
        assert app.number == "20150012345"
        assert app.country == "US"
        assert app.kind_code == "A1"
        assert app.display() == "US 2015/0012345 A1"
        assert str(app) == "US20150012345A1"

    def test_can_handle_us_in_display_form(self):
        pat = parse("US 6,013,599 B2")
        assert pat.number == "6013599"
        assert pat.country == "US"
        assert pat.kind_code == "B2"
        assert pat.display() == "US 6,013,599 B2"
        assert str(pat) == "US6013599B2"

        app = parse("US 2015/0012345 A1")
        assert app.number == "20150012345"
        assert app.country == "US"
        assert app.kind_code == "A1"
        assert app.display() == "US 2015/0012345 A1"
        assert str(app) == "US20150012345A1"

    def test_can_handle_us_application_number(self):
        app = parse("14123456")
        assert app.number == "14123456"
        assert app.country == "US"
        assert app.kind_code == ""
        assert app.display() == "US 14/123,456"
        assert str(app) == "US14123456"

        app = parse("US14123456")
        assert app.number == "14123456"
        assert app.country == "US"
        assert app.kind_code == ""
        assert app.display() == "US 14/123,456"
        assert str(app) == "US14123456"

        app = parse("14/123,456")
        assert app.number == "14123456"
        assert app.country == "US"
        assert app.kind_code == ""
        assert app.display() == "US 14/123,456"
        assert str(app) == "US14123456"

        app = parse("14/123456")
        assert app.number == "14123456"
        assert app.country == "US"
        assert app.kind_code == ""
        assert app.display() == "US 14/123,456"
        assert str(app) == "US14123456"

        app = parse("US 14/123,456")
        assert app.number == "14123456"
        assert app.country == "US"
        assert app.kind_code == ""
        assert app.display() == "US 14/123,456"
        assert str(app) == "US14123456"

        app = parse(14123456)
        assert app.number == "14123456"
        assert app.country == "US"
        assert app.kind_code == ""
        assert app.display() == "US 14/123,456"
        assert str(app) == "US14123456"

    def test_can_handle_reissue_applications(self):
        app = parse("RE43633")
        assert app.country == "US"
        assert app.number == "RE43633"
        assert app.kind_code == "E1"
        assert app.display() == "US RE43633 E1"
        assert str(app) == "USRE43633E1"

        app = parse("USRE43633")
        assert app.country == "US"
        assert app.number == "RE43633"
        assert app.kind_code == "E1"
        assert app.display() == "US RE43633 E1"
        assert str(app) == "USRE43633E1"

    def test_can_handle_pct_applications(self):
        app = parse("PCT/US17/36577")
        assert app.type == "international application"
        assert app.country == "US"
        assert app.number == "036577"
        assert app.year == "2017"
        assert app.kind_code == ""
        assert app.display() == "PCT/US17/36577"
        assert str(app) == "PCTUS2017036577"

        app = parse("PCT/US2017/036577")
        assert app.type == "international application"
        assert app.country == "US"
        assert app.number == "036577"
        assert app.year == "2017"
        assert app.kind_code == ""
        assert app.display(style="new") == "PCT/US2017/036577"
        assert app.display() == "PCT/US17/36577"
        assert str(app) == "PCTUS2017036577"
    
    def test_can_handle_canadian_patents(self):
        app = parse("CA2967774A")
        assert app.type == "application"
        assert app.country == "CA"
        assert app.number == "2967774"
        assert app.kind_code == "A"
        assert app.display() == "CA 2967774 A"
        assert str(app) == "CA2967774A"

        app = parse("2967774", country='CA')
        assert app.type == "application"
        assert app.country == "CA"
        assert app.number == "2967774"
        assert app.kind_code == "A"
        assert app.display() == "CA 2967774 A"
        assert str(app) == "CA2967774A"

        app = parse("CA2967774A1")
        assert app.country == "CA"
        assert app.number == "2967774"
        assert app.kind_code == "A1"
        assert app.type == "publication"
        assert app.display() == "CA 2967774 A1"
        assert str(app) == "CA2967774A1"

        app = parse("CA2967774E")
        assert app.country == "CA"
        assert app.number == "2967774"
        assert app.kind_code == "E"
        assert app.type == "reissue patent"
        assert app.display() == "CA 2967774 E"
        assert str(app) == "CA2967774E"
