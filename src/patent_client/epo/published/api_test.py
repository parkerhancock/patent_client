import json
from pathlib import Path

import pytest

from patent_client.util.test import compare_dicts

from .api import PublishedApi

expected_dir = Path(__file__).parent / "test" / "expected"


def test_doc_example_biblio():
    result = PublishedApi.biblio.get_biblio("EP1000000.A1", format="epodoc")
    expected_file = (expected_dir / "ep1000000_biblio_result.json")
    #expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_doc_example_full_cycle():
    result = PublishedApi.biblio.get_full_cycle("EP1000000.A1", format="epodoc")
    expected_file = (expected_dir / "ep1000000_full_cycle_result.json")
    #expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_doc_example_abstract():
    result = PublishedApi.biblio.get_abstract("EP1000000.A1", format="epodoc")
    expected_file = (expected_dir / "ep1000000_abstract_result.json")
    #expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_doc_example_abstract():
    result = PublishedApi.biblio.get_abstract("EP1000000.A1", format="epodoc")
    expected_file = (expected_dir / "ep1000000_abstract_result.json")
    #expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_search():
    result = PublishedApi.search.search("ti=plastic")
    with pytest.warns(None, match=r"OPS stops counting"):
        assert len(result) == 10000

    sample = result[5:10]
    assert len(sample) == 5


def test_search():
    with pytest.warns(None, match=r"OPS stops counting"):
        result = PublishedApi.search.search("ti=plastic")
        assert result.num_results == 10000


def test_description():
    result = PublishedApi.fulltext.get_description("EP1000000.A1", format="epodoc")
    expected_file = expected_dir / "ep1000000_description_result.json"
    #expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)


def test_claims():
    result = PublishedApi.fulltext.get_claims("EP1000000.A1", format="epodoc")
    expected_file = expected_dir / "ep1000000_claims_result.json"
    #expected_file.write_text(result.to_json(indent=2))
    expected = json.loads(expected_file.read_text())
    compare_dicts(json.loads(result.to_json()), expected)
