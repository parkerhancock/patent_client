import pytest

from .manager import USApplicationBiblioManager, USApplicationManager


@pytest.mark.asyncio
async def test_all_apps():
    manager = USApplicationManager().filter(query=dict())
    assert await manager.count() > 1000


@pytest.mark.asyncio
async def test_get_one_app():
    app = await USApplicationManager().get(q="applicationNumberText:16123456")
    assert app is not None
    assert app.appl_id == "16123456"


@pytest.mark.asyncio
async def test_get_app_from_search_result():
    manager = USApplicationBiblioManager()
    result = await manager.get(q="applicationNumberText:16123456")
    application = await result.application
    assert application.appl_id == "16123456"


@pytest.mark.asyncio
async def test_get_app_biblio_from_search_result():
    manager = USApplicationBiblioManager()
    result = await manager.get(q="applicationNumberText:16123456")
    biblio = await result.biblio
    assert biblio.appl_id == "16123456"


@pytest.mark.asyncio
async def test_get_continuity_from_search_result():
    manager = USApplicationBiblioManager()
    result = await manager.get(q="applicationNumberText:16123456")
    continuity = await result.continuity
    assert len(continuity.child_continuity) > 0


@pytest.mark.asyncio
async def test_get_documents_from_search_result():
    manager = USApplicationBiblioManager()
    result = await manager.get(q="applicationNumberText:16123456")
    documents = await result.documents
    assert await documents.count() > 0


@pytest.mark.asyncio
async def test_simple_keyword_searches():
    manager = USApplicationManager()
    result = await manager.get("16123456")
    assert result.appl_id == "16123456"


@pytest.mark.asyncio
async def test_combination_search():
    manager = USApplicationManager()
    result = manager.filter(invention_title="Hair Dryer", filing_date_gte="2020-01-01")
    assert await result.count() > 5
