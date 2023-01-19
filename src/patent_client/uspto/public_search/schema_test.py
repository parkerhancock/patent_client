import json
from pathlib import Path

from patent_client.util.test import compare_dicts

from .schema import PublicSearchDocumentSchema
from .schema import PublicSearchSchema

test_dir = Path(__file__).parent / "test"


def test_biblio():
    data = (test_dir / "biblio.json").read_text()
    parser = PublicSearchSchema()
    result = parser.load_batch(data)
    expected_file = test_dir / "biblio_expected.json"
    expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    result_json = json.loads(result.to_json())
    for i in range(len(expected)):
        compare_dicts(expected[i], result_json[i])


def test_docs():
    data = (test_dir / "docs.json").read_text()
    parser = PublicSearchDocumentSchema()
    result = parser.load_batch(data)
    expected_file = test_dir / "docs_expected.json"
    expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    result_json = json.loads(result.to_json())
    for i in range(len(expected)):
        compare_dicts(expected[i], result_json[i])
