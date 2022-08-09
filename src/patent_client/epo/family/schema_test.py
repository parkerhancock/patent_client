import json
from pathlib import Path

import lxml.etree as ET
from patent_client.util.test import compare_dicts

from .schema import FamilySchema

test_dir = Path(__file__).parent / "fixtures" / "examples"
expected_dir = Path(__file__).parent / "fixtures" / "expected"


def test_example():
    tree = ET.parse(test_dir / "example.xml")
    result = FamilySchema().load(tree)
    expected_file = expected_dir / "example.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)
