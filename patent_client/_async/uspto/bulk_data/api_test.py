import pytest

from .api import BulkDataApi
from .model import File, Product


@pytest.mark.asyncio
async def test_can_get_latest():
    latest = await BulkDataApi.get_latest()
    first = latest[0]
    assert isinstance(first, Product)
    assert isinstance(first.files[0], File)


@pytest.mark.asyncio
async def test_can_get_by_short_name():
    first = await BulkDataApi.get_by_short_name("PTGRXML")
    assert isinstance(first, Product)
    assert isinstance(first.files[0], File)


@pytest.mark.asyncio
async def test_can_get_by_short_name_with_date_range():
    first = await BulkDataApi.get_by_short_name(
        "PTGRXML", from_date="2023-06-01", to_date="2023-08-01"
    )
    assert isinstance(first, Product)
    assert isinstance(first.files[0], File)
    assert len(first.files) == 10


@pytest.mark.asyncio
@pytest.mark.no_vcr
@pytest.mark.skip(reason="This test is too slow")
async def test_can_download_file(tmpdir):
    product = await BulkDataApi.get_by_short_name("PTGRXML")
    file = product.files[0]
    await file.adownload(tmpdir)
    assert len(list(tmpdir.listdir())) == 1
