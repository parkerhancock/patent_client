from pathlib import Path

from .api import PublishedApi

expected_dir = Path(__file__).parent / "test" / "expected"


def test_doc_example_biblio():
    result = PublishedApi.biblio.get_biblio("EP1000000.A1", format="epodoc")
    expected_file = expected_dir / "ep1000000_biblio_result.xml"
    # expected_file.write_text(result)
    expected = expected_file.read_text()
    assert result == expected


def test_doc_example_full_cycle():
    result = PublishedApi.biblio.get_full_cycle("EP1000000.A1", format="epodoc")
    expected_file = expected_dir / "ep1000000_full_cycle_result.xml"
    # expected_file.write_text(result)
    expected = expected_file.read_text()
    assert result == expected


def test_doc_example_abstract():
    result = PublishedApi.biblio.get_abstract("EP1000000.A1", format="epodoc")
    expected_file = expected_dir / "ep1000000_abstract_result.xml"
    # expected_file.write_text(result)
    expected = expected_file.read_text()
    assert result == expected


def test_search():
    result = PublishedApi.search.search("ti=plastic")
    expected_file = expected_dir / "search_result.xml"
    # expected_file.write_text(result)
    expected = expected_file.read_text()
    assert result == expected


def test_description():
    result = PublishedApi.fulltext.get_description("EP1000000.A1", format="epodoc")
    expected_file = expected_dir / "ep1000000_description_result.xml"
    # expected_file.write_text(result)
    expected = expected_file.read_text()
    assert result == expected


def test_claims():
    result = PublishedApi.fulltext.get_claims("EP1000000.A1", format="epodoc")
    expected_file = expected_dir / "ep1000000_claims_result.xml"
    # expected_file.write_text(result)
    expected = expected_file.read_text()
    assert result == expected
