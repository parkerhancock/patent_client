import json
from pathlib import Path

from .convert.biblio import PublicSearchBiblioPageSchema
from .convert.document import PublicSearchDocumentSchema

fixtures = Path(__file__).parent / "fixtures"


def test_convert_biblio():
    input_file = fixtures / "biblio.json"
    output_file = fixtures / "biblio_convert.json"
    input_data = json.loads(input_file.read_text())
    output_data = PublicSearchBiblioPageSchema().deserialize(input_data)
    # output_file.write_text(output_data.to_json(indent=2))
    expected_data = json.loads(output_file.read_text())
    assert json.loads(output_data.to_json()) == expected_data


def test_convert_doc():
    input_file = fixtures / "doc.json"
    output_file = fixtures / "doc_convert.json"
    input_data = json.loads(input_file.read_text())
    output_data = PublicSearchDocumentSchema().load_batch(input_data)
    output_file.write_text(output_data.to_json(indent=2))
    expected_data = json.loads(output_file.read_text())
    assert json.loads(output_data.to_json()) == expected_data
