import json
from pathlib import Path

import pytest

from .api import FamilyAsyncApi

fixtures = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_api():
    result = await FamilyAsyncApi.get_family("EP1000000A1")
    expected_file = fixtures / "family_api_output.json"
    # expected_file.write_text(result.model_dump_json(indent=2))
    expected = expected_file.read_text()
    assert json.loads(expected) == json.loads(result.model_dump_json())
