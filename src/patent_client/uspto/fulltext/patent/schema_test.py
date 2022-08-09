from pathlib import Path

import lxml.etree as ET

from .schema import PatentResultPageSchema

example_dir = Path(__file__).parent / "test"


def test_patent_result_schema():
    text = (example_dir / "pat_search.html").read_text()
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
