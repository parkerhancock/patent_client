import json
from pathlib import Path

import lxml.etree as ET

from patent_client.util.test import compare_dicts

from .schema import LegalSchema

fixture_dir = Path(__file__).parent / "fixtures"


def test_example_1():
    tree = ET.parse(fixture_dir / "example_1.xml")
    result = LegalSchema().load(tree)
    expected_file = fixture_dir / "example_1_convert.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_example_2():
    tree = ET.parse(fixture_dir / "example_2.xml")
    result = LegalSchema().load(tree)
    expected_file = fixture_dir / "example_2_convert.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_example_3():
    tree = ET.parse(fixture_dir / "example_3.xml")
    result = LegalSchema().load(tree)
    expected_file = fixture_dir / "example_3_convert.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)
