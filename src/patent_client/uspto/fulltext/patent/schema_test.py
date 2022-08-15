import json
from pathlib import Path

import lxml.etree as ET
import pytest

from .schema import PatentResultPageSchema
from .schema import PatentSchema

fixture_dir = Path(__file__).parent / "fixtures"


def test_patent_result_schema():
    text = (fixture_dir / "pat_search.html").read_text()
    tree = ET.HTML(text)
    schema = PatentResultPageSchema()
    result = schema.load(tree)
    assert result.num_results == 830
    assert result.start == 1
    assert result.end == 50
    assert len(result.results) == 50
    assert result.query == "(CCL/166/308.1 AND APD/19000101->20121005)"
    record = result.results[49]
    assert record.seq == 50
    assert record.publication_number == "8875790"
    assert record.title == "Method and system for fracking and completing wells"


locked = [
    "pat_3113620",
    "pat_5439055",
    "pat_5890536",
    "pat_6095611",
    "pat_6103599",
    "pat_6460641",
    "pat_7752445",
    "pat_8645300",
    "pat_8832265",
    "pat_9140110",
    "pat_10000000",
    "pat_D645062",
    "pat_RE43663",
]


@pytest.mark.parametrize("patent_file", sorted(fixture_dir.glob("patents/*.html")), ids=lambda p: p.stem)
def test_patent_schema(patent_file):
    schema = PatentSchema()
    result = schema.load(patent_file.read_text())
    expected_file = patent_file.parent / (patent_file.stem + ".json")
    if patent_file.stem not in locked:
        expected_file.write_text(result.to_json(indent=2))
    assert json.loads(expected_file.read_text()) == json.loads(result.to_json())
