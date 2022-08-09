import json
from pathlib import Path

from patent_client.util.test import compare_dicts

from .api import FamilyApi

test_dir = Path(__file__).parent / "fixtures" / "examples"
expected_dir = Path(__file__).parent / "fixtures" / "expected"


def test_example():
    result = FamilyApi.get_family("EP1000000A1")
    expected = json.loads((expected_dir / "example.json").read_text())
    compare_dicts(json.loads(result.to_json()), expected)
