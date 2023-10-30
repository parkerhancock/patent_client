from pathlib import Path

import pytest

from .api import PublishedApi
from .api import PublishedAsyncApi

expected_dir = Path(__file__).parent / "test" / "expected"


class TestPublishedBiblioApi:
    def test_doc_example_biblio(self):
        result = PublishedApi.biblio.get_biblio("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_biblio_result.xml"
        expected_file.write_text(result, encoding="utf8")
        expected = expected_file.read_text(encoding="utf8")
        assert result == expected

    def test_doc_example_full_cycle(self):
        result = PublishedApi.biblio.get_full_cycle("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_full_cycle_result.xml"
        expected_file.write_text(result, encoding="utf8")
        expected = expected_file.read_text(encoding="utf8")
        assert result == expected

    def test_doc_example_abstract(self):
        result = PublishedApi.biblio.get_abstract("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_abstract_result.xml"
        expected_file.write_text(result, encoding="utf8")
        expected = expected_file.read_text(encoding="utf8")
        assert result == expected


class TestPublishedBiblioAsyncApi:
    @pytest.mark.asyncio
    async def test_doc_example_biblio(self):
        result = await PublishedAsyncApi.biblio.get_biblio("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_biblio_result.xml"
        expected_file.write_text(result, encoding="utf8")
        expected = expected_file.read_text(encoding="utf8")
        assert result == expected

    @pytest.mark.asyncio
    async def test_doc_example_full_cycle(self):
        result = await PublishedAsyncApi.biblio.get_full_cycle("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_full_cycle_result.xml"
        expected_file.write_text(result, encoding="utf8")
        expected = expected_file.read_text(encoding="utf8")
        assert result == expected

    @pytest.mark.asyncio
    async def test_doc_example_abstract(self):
        result = await PublishedAsyncApi.biblio.get_abstract("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_abstract_result.xml"
        expected_file.write_text(result, encoding="utf8")
        expected = expected_file.read_text(encoding="utf8")
        assert result == expected


class TestSearchApi:
    def test_search(self):
        result = PublishedApi.search.search("ti=plastic")
        expected_file = expected_dir / "search_result.xml"
        # expected_file.write_text(result)
        expected = expected_file.read_text()
        assert result == expected


class TestSearchApi:
    @pytest.mark.asyncio
    async def test_search(self):
        result = await PublishedAsyncApi.search.search("ti=plastic")
        expected_file = expected_dir / "search_result.xml"
        # expected_file.write_text(result)
        expected = expected_file.read_text()
        assert result == expected


class TestFullTextApi:
    def test_description(self):
        result = PublishedApi.fulltext.get_description("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_description_result.xml"
        # expected_file.write_text(result)
        expected = expected_file.read_text()
        assert result == expected

    def test_claims(self):
        result = PublishedApi.fulltext.get_claims("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_claims_result.xml"
        # expected_file.write_text(result)
        expected = expected_file.read_text()
        assert result == expected


class TestFullTextAsyncApi:
    @pytest.mark.asyncio
    async def test_description(self):
        result = await PublishedAsyncApi.fulltext.get_description("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_description_result.xml"
        # expected_file.write_text(result)
        expected = expected_file.read_text()
        assert result == expected

    @pytest.mark.asyncio
    async def test_claims(self):
        result = await PublishedAsyncApi.fulltext.get_claims("EP1000000.A1", format="epodoc")
        expected_file = expected_dir / "ep1000000_claims_result.xml"
        # expected_file.write_text(result)
        expected = expected_file.read_text()
        assert result == expected
