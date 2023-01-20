import pytest

from .query import QueryBuilder
from .query import QueryException

builder = QueryBuilder()


def test_garbage():
    with pytest.raises(QueryException):
        builder.build_query("garbage")


def test_default():
    assert builder.build_query("12123456") == {
        "doc_number": "12123456",
        "type_code": "application",
        "office_code": "US",
    }


def test_us_string_queries():
    assert builder.build_query("RE12345") == {"doc_number": "RE12345", "type_code": "patent", "office_code": "US"}
    assert builder.build_query("1234567") == {"doc_number": "1234567", "type_code": "patent", "office_code": "US"}
    assert builder.build_query("1234567123456") == {
        "doc_number": "1234567123456",
        "type_code": "patent",
        "office_code": "US",
    }


def test_us_string_queries_with_country():
    assert builder.build_query("USRE12345") == {"doc_number": "RE12345", "type_code": "patent", "office_code": "US"}
    assert builder.build_query("US1234567") == {"doc_number": "1234567", "type_code": "patent", "office_code": "US"}
    assert builder.build_query("US1234567123456") == {
        "doc_number": "1234567123456",
        "type_code": "patent",
        "office_code": "US",
    }


def test_us_string_queries_with_defined_type():
    assert builder.build_query("US16123456", type="application") == {
        "doc_number": "16123456",
        "type_code": "application",
        "office_code": "US",
    }
    assert builder.build_query("US16123456", type="patent") == {
        "doc_number": "16123456",
        "type_code": "patent",
        "office_code": "US",
    }


def test_indefinite_us_string_queries():
    with pytest.raises(QueryException):
        builder.build_query("US16123456")
    with pytest.raises(QueryException):
        builder.build_query("12345678910")


def test_wipo_queries():
    assert builder.build_query("PCT/US15/12345") == {
        "doc_number": "PCT/US15/12345",
        "type_code": "application",
        "office_code": "WIPO",
    }
    assert builder.build_query("WO1234567") == {
        "doc_number": "WO1234567",
        "type_code": "publication",
        "office_code": "WIPO",
    }
    assert builder.build_query(application="PCT/US15/12345") == {
        "doc_number": "PCT/US15/12345",
        "type_code": "application",
        "office_code": "WIPO",
    }
    assert builder.build_query(publication="WO1234567") == {
        "doc_number": "WO1234567",
        "type_code": "publication",
        "office_code": "WIPO",
    }
    with pytest.raises(QueryException):
        assert builder.build_query(publication="PCT/US15/12345") == {
            "doc_number": "PCT/US15/12345",
            "type_code": "application",
            "office_code": "WIPO",
        }
    with pytest.raises(QueryException):
        assert builder.build_query(application="WO1234567") == {
            "doc_number": "WO1234567",
            "type_code": "publication",
            "office_code": "WIPO",
        }


def test_au_queries():
    with pytest.raises(QueryException):
        builder.build_query("AU123456")
    assert builder.build_query("AU123456", type="publication") == {
        "doc_number": "AU123456",
        "type_code": "publication",
        "office_code": "CASE",
    }
    assert builder.build_query("AU123456", type="application") == {
        "doc_number": "AU123456",
        "type_code": "application",
        "office_code": "CASE",
    }
    assert builder.build_query(application="AU123456") == {
        "doc_number": "AU123456",
        "type_code": "application",
        "office_code": "CASE",
    }
    assert builder.build_query(publication="AU123456") == {
        "doc_number": "AU123456",
        "type_code": "publication",
        "office_code": "CASE",
    }


def test_ep_queries():
    assert builder.build_query("EP1234567") == {
        "office_code": "EP",
        "doc_number": "1234567",
        "type_code": "publication",
    }
    assert builder.build_query("1234567", office="EP") == {
        "office_code": "EP",
        "doc_number": "1234567",
        "type_code": "publication",
    }
    assert builder.build_query(publication="EP1234567") == {
        "office_code": "EP",
        "doc_number": "1234567",
        "type_code": "publication",
    }
    assert builder.build_query(publication="1234567", office="EP") == {
        "office_code": "EP",
        "doc_number": "1234567",
        "type_code": "publication",
    }

    assert builder.build_query("EP12345678") == {
        "office_code": "EP",
        "doc_number": "12345678",
        "type_code": "application",
    }
    assert builder.build_query("12345678", office="EP") == {
        "office_code": "EP",
        "doc_number": "12345678",
        "type_code": "application",
    }
    assert builder.build_query(application="EP12345678") == {
        "office_code": "EP",
        "doc_number": "12345678",
        "type_code": "application",
    }
    assert builder.build_query(application="12345678", office="EP") == {
        "office_code": "EP",
        "doc_number": "12345678",
        "type_code": "application",
    }
