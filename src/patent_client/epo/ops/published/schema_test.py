import json
from pathlib import Path

import lxml.etree as ET
from patent_client.util.test import compare_dicts

from .schema import BiblioResultSchema
from .schema import ClaimsSchema
from .schema import DescriptionSchema
from .schema import ImagesSchema
from .schema import SearchSchema

test_dir = Path(__file__).parent / "test"
expected_dir = Path(__file__).parent / "test" / "expected"


def test_biblio():
    tree = ET.parse(test_dir / "biblio_example.xml")
    result = BiblioResultSchema().load(tree)
    assert len(result.documents) == 1
    d = result.documents[0]
    assert d.title == "Bi-directional steerable catheter control handle"
    assert d.country == "US"
    assert d.doc_number == "2006142694"
    assert d.family_id == "35840242"
    for f in (
        "publication_reference_docdb",
        "publication_reference_epodoc",
        "application_reference_docdb",
        "application_reference_epodoc",
        "application_reference_original",
    ):
        assert hasattr(d, f)
    assert len(d.citations) == 99


def test_claims():
    tree = ET.parse(test_dir / "claims_example.xml")
    result = ClaimsSchema().load(tree)
    example_file = expected_dir / "claims_example.json"
    example_file.write_text(result.to_json(indent=2))
    expected = json.loads(example_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_description():
    tree = ET.parse(test_dir / "description_example.xml")
    result = DescriptionSchema().load(tree)
    assert result.document_id.country == "EP"
    assert result.document_id.doc_number == "1000000"
    assert result.document_id.kind == "A1"
    assert len(result.description) == 10544


def test_search():
    tree = ET.parse(test_dir / "search_example.xml")
    result = SearchSchema().load(tree)
    assert result.query == 'applicant = "nine energy"'
    assert result.num_results == 15
    assert result.begin == 1
    assert result.end == 25
    assert len(result.results) == 15
    r = result.results[3]
    assert r.family_id == "70280448"
    assert r.id_type == "docdb"
    assert r.country == "US"


def test_images():
    tree = ET.parse(test_dir / "image_example.xml")
    result = ImagesSchema().load(tree)
    expected_file = expected_dir / "image_example.json"
    expected_file.write_text(result.to_json())
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_full_cycle():
    tree = ET.parse(test_dir / "full_cycle_example.xml")
    result = BiblioResultSchema().load(tree)
    assert len(result.documents) == 2
    d = result.documents[0]
    assert d.title == "Apparatus for manufacturing green bricks for the brick manufacturing industry"


def test_biblio_2():
    filename = "biblio_example_4"
    input = test_dir / f"{filename}.xml"
    tree = ET.parse(input)
    result = BiblioResultSchema().load(tree)
    expected_file = expected_dir / f"{filename}.json"
    # expected_file.write_text(result.to_json(indent=2))
    compare_dicts(json.loads(result.to_json()), json.loads(expected_file.read_text()))
