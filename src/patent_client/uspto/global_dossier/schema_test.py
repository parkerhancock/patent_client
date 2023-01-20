import json
from pathlib import Path

from patent_client.util.test import compare_dicts

from .schema import DocumentListSchema
from .schema import GlobalDossierSchema

test_dir = Path(__file__).parent / "test"


def test_app():
    data = (test_dir / "app.json").read_text()
    parser = GlobalDossierSchema()
    result = parser.load(data)
    expected_file = test_dir / "app_expected.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    result_json = json.loads(result.to_json())
    compare_dicts(expected, result_json)


def test_doc_list():
    data = (test_dir / "doc_list.json").read_text()
    parser = DocumentListSchema()
    result = parser.load(data)
    expected_file = test_dir / "doc_list_expected.json"
    expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    result_json = json.loads(result.to_json())
    compare_dicts(expected, result_json)
