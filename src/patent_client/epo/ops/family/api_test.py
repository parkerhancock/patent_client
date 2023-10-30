from pathlib import Path

import pytest

from .api import FamilyAsyncApi

test_dir = Path(__file__).parent / "fixtures" / "examples"
expected_dir = Path(__file__).parent / "fixtures" / "expected"


@pytest.mark.asyncio
async def test_async_example():
    result = await FamilyAsyncApi.get_family("EP1000000A1")
    expected_file = expected_dir / "example.xml"
    expected_file.write_text(result)
    expected = expected_file.read_text()
    assert expected == result
