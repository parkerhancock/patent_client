import pytest

from .number_service import NumberServiceApi


@pytest.mark.asyncio
async def test_number_service():
    result = await NumberServiceApi.convert_number("US14123456")
    assert result.find(".//{*}input//{*}doc-number").text == "14123456"
    assert result.find(".//{*}input//{*}country").text == "US"
    assert result.find(".//{*}input//{*}document-id").attrib["document-id-type"] == "original"
    assert result.find(".//{*}output//{*}doc-number").text == "14123456"
    assert result.find(".//{*}output//{*}country").text == "US"
    assert result.find(".//{*}output//{*}document-id").attrib["document-id-type"] == "docdb"
