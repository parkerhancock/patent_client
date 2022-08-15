import json
from pathlib import Path

import lxml.etree as ET
from patent_client.util.test import compare_dicts

from .schema import LegalSchema

test_dir = Path(__file__).parent / "test"
expected_dir = Path(__file__).parent / "test" / "expected"


def test_example():
    tree = ET.parse(test_dir / "example.xml")
    result = LegalSchema().load(tree)
    expected_file = expected_dir / "example.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_us_example():
    tree = ET.parse(test_dir / "us_example.xml")
    result = LegalSchema().load(tree)
    expected_file = expected_dir / "us_example.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)
