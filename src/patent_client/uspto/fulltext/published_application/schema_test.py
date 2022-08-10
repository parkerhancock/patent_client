from pathlib import Path
import json

import lxml.etree as ET

from .schema import PublishedApplicationResultPageSchema, PublishedApplicationSchema
from patent_client.util.test import compare_dicts

example_dir = Path(__file__).parent / "test"
expected_path = Path(__file__).parent / "test" / "expected"

def test_pub_result_schema():
    text = (example_dir / "pub_search.html").read_text()
    tree = ET.HTML(text)
    schema = PublishedApplicationResultPageSchema()
    result = schema.load(tree)
    assert result.num_results == 7716
    assert result.start == 1
    assert result.end == 50
    assert len(result.results) == 50
    assert result.query == "AN/Google"
    record = result.results[49]
    assert record.seq == 50
    assert record.publication_number == "20220200679"
    assert record.title == "Parallel Beamforming Training with Coordinated Base Stations"

def test_pub_schema():
    text = (example_dir / "example_pub.html").read_text()
    tree = ET.HTML(text)
    schema = PublishedApplicationResultPageSchema()
    result = schema.load(tree)
    expected_file = expected_path / "example_pub.json"
    expected_file.write_text(result.to_json(indent=2))
    compare_dicts(json.loads(result.to_json()), json.loads(expected_file.read_text()))
   