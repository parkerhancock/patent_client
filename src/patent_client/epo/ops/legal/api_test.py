from pathlib import Path

import pytest

from .api import LegalAsyncApi

fixtures = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_async_example():
    result = await LegalAsyncApi.get_legal("EP1000000A1")
    assert str(result.publication_reference) == "EP1000000A1"
    assert len(result.events) > 50
