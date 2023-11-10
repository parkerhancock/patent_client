import datetime

import pytest

from .util import date_to_solr_date


class TestDateToSolrDate:
    def test_can_take_string_date(self):
        assert date_to_solr_date("2021-01-01") == "2021-01-01T00:00:00Z"

    def test_can_take_datetime_date(self):
        assert date_to_solr_date(datetime.date(2021, 1, 1)) == "2021-01-01T00:00:00Z"

    def test_can_take_datetime(self):
        assert date_to_solr_date(datetime.datetime(2021, 1, 1, 12, 30, 0)) == "2021-01-01T12:30:00Z"

    def test_rejects_invalid_input(self):
        with pytest.raises(ValueError):
            date_to_solr_date(False)
