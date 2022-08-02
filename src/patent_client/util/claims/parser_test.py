import json
from pathlib import Path

from patent_client.util.test import compare_lists

from .parser import ClaimsParser

example_dir = Path(__file__).parent / "examples"


def test_multiple_dependent_claims():
    file = example_dir / "multiple_dependent.txt"
    text = file.read_text()
    result = ClaimsParser().parse(text)
    expected_file = example_dir / "multiple_dependent.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_lists(json.loads(result.to_json()), expected)


def test_published_claims():
    file = example_dir / "published_claims.txt"
    text = file.read_text()
    result = ClaimsParser().parse(text)
    expected_file = example_dir / "published_claims.json"
    # expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_lists(json.loads(result.to_json()), expected)
