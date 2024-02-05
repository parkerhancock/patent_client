import pytest

from .bulk_data import BulkDataApi


@pytest.mark.anyio
async def test_can_get_latest():
    latest = await BulkDataApi.get_latest()
    assert len(latest) > 25


@pytest.mark.anyio
async def test_can_get_by_short_name():
    result = await BulkDataApi.get_by_short_name("PTGRXML")
    assert result["productShortName"] == "PTGRXML"


@pytest.mark.anyio
async def test_can_get_by_short_name_with_date_range():
    result = await BulkDataApi.get_by_short_name("PTGRXML", from_date="2023-06-01", to_date="2023-08-01")
    assert result["productShortName"] == "PTGRXML"
    assert len(result["productFiles"]) == 10
    assert result["productFiles"][0]["fileReleaseDate"] == "2023-06-06"
    assert result["productFiles"][-1]["fileReleaseDate"] == "2023-08-01"
