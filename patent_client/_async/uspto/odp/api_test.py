import pytest

from .api import ODPApi
from .model import PatentSearchRequest


@pytest.fixture
def odp_api():
    return ODPApi()


@pytest.mark.asyncio
async def test_post_search(odp_api):
    search_request = PatentSearchRequest(q="firstNamedApplicant:STMicroelectronics S.A.")
    response = await odp_api.patent_search.post_search(search_request)
    assert response["count"] > 0, "Expected at least one result"


@pytest.mark.asyncio
async def test_get_search(odp_api):
    search_request = PatentSearchRequest(q="firstNamedApplicant:STMicroelectronics S.A.")
    response = await odp_api.patent_search.get_search(search_request)
    assert response["count"] > 0, "Expected at least one result"


@pytest.mark.asyncio
async def test_get_application_data(odp_api):
    application_id = "15123456"
    application = await odp_api.patent_search.get_application_data(application_id)
    assert application.application_number_text is not None, "Expected patent data"


@pytest.mark.asyncio
async def test_get_application_basic_data(odp_api):
    application_id = "15123456"
    application = await odp_api.patent_search.get_application_biblio_data(application_id)
    assert application.application_number_text is not None, "Expected basic patent data"


@pytest.mark.asyncio
async def test_get_patent_term_adjustment_data(odp_api):
    application_id = "16123456"
    response = await odp_api.patent_search.get_patent_term_adjustment_data(application_id)
    assert response.patent_term_adjustment_data is not None, "Expected patent term adjustment data"


@pytest.mark.asyncio
async def test_get_assignments(odp_api):
    application_id = "15123456"
    response = await odp_api.patent_search.get_assignments(application_id)
    assert len(response) > 0, "Expected at least one assignment"


@pytest.mark.asyncio
async def test_get_attorney_data(odp_api):
    application_id = "15123456"
    response = await odp_api.patent_search.get_attorney_data(application_id)
    assert response.record_attorney is not None, "Expected attorney data"


@pytest.mark.asyncio
async def test_get_continuity_data(odp_api):
    application_id = "15123456"
    response = await odp_api.patent_search.get_continuity_data(application_id)
    assert response.patent_file_wrapper_data_bag is not None, "Expected continuity data"


@pytest.mark.asyncio
async def test_get_foreign_priority_data(odp_api):
    application_id = "16123456"
    response = await odp_api.patent_search.get_foreign_priority_data(application_id)
    assert len(response) > 0, "Expected at least one foreign priority"


@pytest.mark.asyncio
async def test_get_transactions(odp_api):
    application_id = "15123456"
    response = await odp_api.patent_search.get_transactions(application_id)
    assert len(response) > 0, "Expected at least one transaction"


@pytest.mark.asyncio
async def test_get_documents(odp_api):
    application_id = "15123456"
    response = await odp_api.patent_search.get_documents(application_id)
    assert response.document_bag is not None, "Expected at least one document"


# Bulk Data Tests
@pytest.mark.asyncio
async def test_bulk_data_search(odp_api):
    response = await odp_api.bulk_data.get_search(
        q="patent", limit=1, include_files=True, latest=True
    )
    assert response.count > 0, "Expected at least one bulk data product"


@pytest.mark.asyncio
async def test_bulk_data_get_product(odp_api):
    response = await odp_api.bulk_data.get_product(
        product_identifier="PTFWPRE", limit=1, include_files=True, latest=True
    )
    assert response.count > 0, "Expected at least one bulk data product"
