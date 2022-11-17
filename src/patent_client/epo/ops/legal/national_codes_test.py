import datetime

from patent_client.epo.ops.legal import national_codes


def stub_date():
    return datetime.datetime(2022, 8, 1).date()


def test_legal_codes():
    dt = national_codes.current_date
    national_codes.current_date = stub_date
    national_codes.current_date = dt
