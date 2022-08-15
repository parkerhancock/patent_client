import json
from pathlib import Path

import lxml.etree as ET
from patent_client.util.test import compare_dicts

from .schema import PublishedApplicationResultPageSchema
from .schema import PublishedApplicationSchema

example_dir = Path(__file__).parent / "fixtures"
pub_dir = Path(__file__).parent / "fixtures" / "pubs"


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
    text = (pub_dir / "pub_20200000001.html").read_text()
    tree = ET.HTML(text)
    schema = PublishedApplicationSchema()
    result = schema.load(tree)
    expected_file = pub_dir / "pub_20200000001.json"
    expected_file.write_text(result.to_json(indent=2))
    compare_dicts(json.loads(result.to_json()), json.loads(expected_file.read_text()))
