import pytest

from .legal import LegalApi


@pytest.mark.anyio
async def test_get_legal():
    result = await LegalApi.get_legal("EP1000000A1")
    assert len(result.findall(".//{http://ops.epo.org}legal")) >= 50


@pytest.mark.anyio
async def test_get_legal_code_spreadsheet():
    result = await LegalApi.get_legal_code_spreadsheet()
    assert len(result.xpath(".//tr/td[contains(text(), 'Legal event codes')]/../td[4]")) > 0
