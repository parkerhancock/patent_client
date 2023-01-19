import pytest
from dateutil.parser import parse as parse_dt

from .manager import PatentBiblioManager
from .query import QueryException


def test_default_query():
    assert PatentBiblioManager().filter("6103599")._query == '"6103599".PN.'


def test_plural_default_query():
    assert PatentBiblioManager().filter("6103599", "6103600")._query == '("6103599" "6103600").PN.'


def test_keyword_query():
    assert PatentBiblioManager().filter(appl_id="6103599")._query == '"6103599".APNR.'


def test_plural_keyword_query():
    assert PatentBiblioManager().filter(appl_id=("11111111", "11222222"))._query == '("11111111" "11222222").APNR.'


def test_keyword_date_query():
    assert PatentBiblioManager().filter(app_filing_date="2021-01-01")._query == '@APD="20210101"'
    assert PatentBiblioManager().filter(app_filing_date=parse_dt("2021-01-01"))._query == '@APD="20210101"'
    assert PatentBiblioManager().filter(app_filing_date=parse_dt("2021-01-01").date())._query == '@APD="20210101"'


def test_keyword_date_range_query():
    assert PatentBiblioManager().filter(app_filing_date="2021-01-01->2021-02-01")._query == "@APD>=20210101<=20210201"
    assert (
        PatentBiblioManager().filter(app_filing_date__range=("2021-01-01", "2021-02-01"))._query
        == "@APD>=20210101<=20210201"
    )
    assert (
        PatentBiblioManager().filter(app_filing_date__range=(parse_dt("2021-01-01"), parse_dt("2021-02-01")))._query
        == "@APD>=20210101<=20210201"
    )


def test_date_operator_queries():
    assert PatentBiblioManager().filter(app_filing_date__gt="2021-01-01")._query == '@APD>"20210101"'
    assert PatentBiblioManager().filter(app_filing_date__gte="2021-01-01")._query == '@APD>="20210101"'
    assert PatentBiblioManager().filter(app_filing_date__lt="2021-01-01")._query == '@APD<"20210101"'
    assert PatentBiblioManager().filter(app_filing_date__lte="2021-01-01")._query == '@APD<="20210101"'


def test_error_query():
    with pytest.raises(QueryException):
        PatentBiblioManager().filter(blargh="2021-01-01")._query


def test_error_date_query():
    with pytest.raises(QueryException):
        q = PatentBiblioManager().filter(app_filing_date="2021-00-01")._query
    with pytest.raises(QueryException):
        q = PatentBiblioManager().filter(app_filing_date=False)._query


def test_multiple_fields():
    assert (
        PatentBiblioManager().filter("6103599", app_filing_date="2021-01-01")._query
        == '@APD="20210101" AND "6103599".PN.'
    )
    assert (
        PatentBiblioManager().filter("6103599").filter(app_filing_date="2021-01-01")._query
        == '"6103599".PN. AND @APD="20210101"'
    )
    assert (
        PatentBiblioManager().filter(patent_number="6103599", app_filing_date="2021-01-01")._query
        == '@APD="20210101" AND "6103599".PN.'
    )


def test_raw_query():
    assert PatentBiblioManager().filter(query="example query")._query == "example query"


def test_raw_query_with_keywords():
    assert (
        PatentBiblioManager().filter(query="some text", patent_number="6103599")._query == '"6103599".PN. AND some text'
    )


def test_default_or():
    assert (
        PatentBiblioManager().option(default_operator="OR").filter(patent_number="6103599", appl_id="1234567")._query
        == '"1234567".APNR. OR "6103599".PN.'
    )
