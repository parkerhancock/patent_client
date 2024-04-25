import datetime

import pytest

from ..legal import national_codes


def stub_date():
    return datetime.datetime(2022, 8, 1).date()


def test_legal_codes():
    dt = national_codes.current_date
    national_codes.current_date = stub_date
    national_codes.current_date = dt


@pytest.mark.asyncio
async def test_epo_website_parsing():
    sp_date, sp_url = await national_codes.get_spreadsheet_from_epo_website()
    assert isinstance(sp_date, datetime.date)
    assert isinstance(sp_url, str)
