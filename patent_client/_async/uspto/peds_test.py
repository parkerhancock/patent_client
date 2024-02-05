import pytest

from .peds import PatentExaminationDataSystemApi


@pytest.mark.anyio
async def test_can_get_app():
    result = await PatentExaminationDataSystemApi.create_query("applId:(16123456)")
    assert result["queryResults"]["searchResponse"]["response"]["numFound"] == 1
    assert result["queryResults"]["searchResponse"]["response"]["docs"][0]["applId"] == "16123456"


@pytest.mark.anyio
async def test_can_search_by_customer_number():
    result = await PatentExaminationDataSystemApi().create_query("appCustNumber:(70155)")
    assert result["queryResults"]["searchResponse"]["response"]["numFound"] > 10


@pytest.mark.anyio
async def test_can_limit_by_rows():
    result = await PatentExaminationDataSystemApi().create_query("appCustNumber:(70155)", rows=5)
    assert result["queryResults"]["searchResponse"]["response"]["numFound"] >= 5
