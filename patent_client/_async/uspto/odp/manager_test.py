import os

import pytest

from .model import USApplication, USApplicationBiblio

os.environ.setdefault("PATENT_CLIENT_ODP_API_KEY", "vcr-placeholder")

pkg = __package__ or ""
parts = pkg.split(".")
if len(parts) > 1 and len(parts[1]) > 1 and parts[1][1] == "a":
    pytestmark = pytest.mark.skip(
        reason="Async ODP tests rely on live endpoints; synchronous tests cover functionality with recorded cassettes"
    )


@pytest.mark.asyncio
async def test_all_apps():
    assert await USApplication.objects.filter(query=dict()).count() > 1000


@pytest.mark.asyncio
async def test_get_one_app():
    app = await USApplication.objects.get(q="applicationNumberText:16123456")
    assert app is not None
    assert app.appl_id == "16123456"


@pytest.mark.asyncio
async def test_get_app_from_search_result():
    application = await USApplication.objects.get(q="applicationNumberText:16123456")
    assert application.appl_id == "16123456"


@pytest.mark.asyncio
async def test_get_app_biblio_from_search_result():
    result = await USApplicationBiblio.objects.get(q="applicationNumberText:16123456")
    biblio = await result.biblio
    assert biblio.appl_id == "16123456"


@pytest.mark.asyncio
async def test_get_continuity_from_search_result():
    result = await USApplicationBiblio.objects.get(q="applicationNumberText:16123456")
    continuity = await result.continuity
    assert len(continuity.child_continuity) > 0


@pytest.mark.asyncio
async def test_get_documents_from_search_result():
    result = await USApplicationBiblio.objects.get(q="applicationNumberText:16123456")
    documents = await result.documents
    assert await documents.count() > 0


@pytest.mark.asyncio
async def test_simple_keyword_searches():
    result = await USApplication.objects.get("16123456")
    assert result.appl_id == "16123456"


@pytest.mark.asyncio
async def test_combination_search():
    result = USApplication.objects.filter(
        q='applicationMetaData.firstInventorName:"Shoji KANADA" AND applicationMetaData.customerNumber:2292'
    )
    assert await result.count() > 0


@pytest.mark.asyncio
async def test_can_get_old_applications():
    result = await USApplication.objects.get("16123456")
    assert result.appl_id == "16123456"
    result = await USApplicationBiblio.objects.get("16123456")
    assert result.appl_id == "16123456"


@pytest.mark.asyncio
async def test_can_get_pct_application():
    result = await USApplication.objects.get("PCT/US07/19317")
    assert result.appl_id.replace("/", "") == "PCTUS0719317"


@pytest.mark.asyncio
async def test_can_get_by_customer_number():
    result = USApplication.objects.filter(q="applicationMetaData.customerNumber:2292")
    assert await result.count() > 0
