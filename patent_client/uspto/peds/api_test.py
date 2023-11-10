import pytest

from .api import PatentExaminationDataSystemApi


@pytest.mark.asyncio
async def test_can_get_app():
    result = await PatentExaminationDataSystemApi().create_query("applId:(16123456)")
    assert result.num_found == 1
    assert result.applications[0].appl_id == "16123456"


@pytest.mark.asyncio
async def test_can_search_by_customer_number():
    result = await PatentExaminationDataSystemApi().create_query("appCustNumber:(70155)")
    assert result.num_found > 10


@pytest.mark.asyncio
async def test_can_limit_by_rows():
    result = await PatentExaminationDataSystemApi().create_query("appCustNumber:(70155)", rows=5)
    assert len(result.applications) == 5
