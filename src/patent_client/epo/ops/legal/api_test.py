from pathlib import Path

import pytest

from .api import LegalApi
from .api import LegalAsyncApi

test_dir = Path(__file__).parent / "test"
expected_dir = Path(__file__).parent / "test" / "expected"


def test_example():
    result = LegalApi.get_legal("EP1000000A1")
    expected_file = expected_dir / "example.xml"
    expected_file.write_text(result)
    expected = expected_file.read_text()
    assert expected == result


@pytest.mark.asyncio
async def test_async_example():
    result = await LegalAsyncApi.get_legal("EP1000000A1")
    expected_file = expected_dir / "example.xml"
    expected_file.write_text(result)
    expected = expected_file.read_text()
    assert expected == result
