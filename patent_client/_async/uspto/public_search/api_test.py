import pytest

from .api import PublicSearchApi


@pytest.mark.asyncio
async def test_simple_search():
    api = PublicSearchApi()
    results = await api.run_query(
        query='("6013599").pn.',
    )
    assert results.num_found == 1
    assert results.docs[0].publication_number == "6013599"
