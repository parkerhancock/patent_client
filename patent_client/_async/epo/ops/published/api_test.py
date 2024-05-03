import json
from pathlib import Path

import pytest

from .api import PublishedApi

fixture_dir = Path(__file__).parent / "fixtures"


class TestPublishedBiblioApi:
    @pytest.mark.asyncio
    async def test_doc_example_biblio(self):
        result = await PublishedApi.biblio.get_biblio("EP1000000.A1", format="epodoc")
        expected_file = fixture_dir / "ep1000000_biblio_result.json"
        expected_file.write_text(result.model_dump_json(indent=2))
        expected = json.loads(expected_file.read_text())
        actual = json.loads(result.model_dump_json())
        assert actual == expected

    @pytest.mark.asyncio
    async def test_doc_example_full_cycle(self):
        result = await PublishedApi.biblio.get_full_cycle("EP1000000.A1", format="epodoc")
        expected_file = fixture_dir / "ep1000000_full_cycle_result.xml"
        expected_file.write_text(result, encoding="utf8")
        expected = expected_file.read_text(encoding="utf8")
        assert result == expected

    @pytest.mark.asyncio
    async def test_doc_example_abstract(self):
        result = await PublishedApi.biblio.get_abstract("EP1000000.A1", format="epodoc")
        expected_file = fixture_dir / "ep1000000_abstract_result.xml"
        # expected_file.write_text(result, encoding="utf8")
        expected = expected_file.read_text(encoding="utf8")
        assert result == expected


class TestSearchApi:
    @pytest.mark.asyncio
    async def test_search(self):
        result = await PublishedApi.search.search("ti=plastic")
        expected_file = fixture_dir / "search_result.xml"
        expected_file.write_text(result.model_dump_json(indent=2))
        expected = json.loads(expected_file.read_text())
        actual = json.loads(result.model_dump_json())
        assert actual == expected


class TestFullTextAsyncApi:
    @pytest.mark.asyncio
    async def test_description(self):
        result = await PublishedApi.fulltext.get_description("EP1000000.A1", format="epodoc")
        expected_file = fixture_dir / "ep1000000_description_result.xml"
        # expected_file.write_text(result.model_dump_json(indent=2))
        expected = json.loads(expected_file.read_text())
        actual = json.loads(result.model_dump_json())
        assert actual == expected

    @pytest.mark.asyncio
    async def test_claims(self):
        result = await PublishedApi.fulltext.get_claims("EP1000000.A1", format="epodoc")
        expected_file = fixture_dir / "ep1000000_claims_result.json"
        # expected_file.write_text(result.model_dump_json(indent=2))
        expected = json.loads(expected_file.read_text())
        actual = json.loads(result.model_dump_json())
        assert actual == expected
