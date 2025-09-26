import os

import pytest

from .api import ODPApi
from .model import SearchRequest

os.environ.setdefault("PATENT_CLIENT_ODP_API_KEY", "vcr-placeholder")

pkg = __package__ or ""
parts = pkg.split(".")
if len(parts) > 1 and len(parts[1]) > 1 and parts[1][1] == "a":
    pytestmark = pytest.mark.skip(
        reason="Async ODP tests rely on live endpoints; synchronous tests cover functionality with recorded cassettes"
    )


@pytest.fixture
def odp_api():
    return ODPApi()


@pytest.mark.asyncio
async def test_post_search(odp_api):
    search_request = SearchRequest(q="firstNamedApplicant:STMicroelectronics S.A.")
    response = await odp_api.post_search(search_request)
    assert response["count"] > 0, "Expected at least one result"


@pytest.mark.asyncio
async def test_get_search(odp_api):
    search_request = SearchRequest(q="firstNamedApplicant:STMicroelectronics S.A.")
    response = await odp_api.get_search(search_request)
    assert response["count"] > 0, "Expected at least one result"


@pytest.mark.asyncio
async def test_get_application_data(odp_api):
    application_id = "16123456"
    application = await odp_api.get_application_data(application_id)
    assert application.appl_id is not None, "Expected patent data"


@pytest.mark.asyncio
async def test_get_application_basic_data(odp_api):
    application_id = "16123456"
    application = await odp_api.get_application_biblio_data(application_id)
    assert application.appl_id is not None, "Expected basic patent data"


@pytest.mark.asyncio
async def test_get_patent_term_adjustment_data(odp_api):
    application_id = "16123456"
    response = await odp_api.get_patent_term_adjustment_data(application_id)
    assert response.adjustment_total_quantity is not None, "Expected patent term adjustment data"


@pytest.mark.asyncio
async def test_get_assignments(odp_api):
    application_id = "16123456"
    response = await odp_api.get_assignments(application_id)
    assert len(response) > 0, "Expected at least one assignment"


@pytest.mark.asyncio
async def test_get_attorney_data(odp_api):
    application_id = "16123456"
    response = await odp_api.get_attorney_data(application_id)
    assert response.attorneys is not None, "Expected attorney data"


@pytest.mark.asyncio
async def test_get_continuity_data(odp_api):
    application_id = "16123456"
    response = await odp_api.get_continuity_data(application_id)
    assert response.parent_continuity is not None, "Expected continuity data"


@pytest.mark.asyncio
async def test_get_foreign_priority_data(odp_api):
    application_id = "16123456"
    response = await odp_api.get_foreign_priority_data(application_id)
    assert len(response) > 0, "Expected at least one foreign priority"


@pytest.mark.asyncio
async def test_get_transactions(odp_api):
    application_id = "16123456"
    response = await odp_api.get_transactions(application_id)
    assert isinstance(response, list)


@pytest.mark.asyncio
async def test_get_documents(odp_api):
    application_id = "16123456"
    response = await odp_api.get_documents(application_id)
    assert len(response) > 0, "Expected at least one document"
