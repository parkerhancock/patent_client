import json
from pathlib import Path

import pytest

from patent_client.util.test import compare_dicts

from .model import Family

fixtures = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_model():
    result = await Family.objects.get("EP1000000A1")
    expected_file = fixtures / "family_model_output.json"
    # expected_file.write_text(result.model_dump_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.model_dump_json()), expected)
