import pytest

from .number_service import NumberServiceApi


@pytest.mark.asyncio
def test_number_service():
    result = await NumberServiceApi.get_number("US14123456")
    assert result.number == "14123456"
    assert result.country == "US"
    assert result.kind_code == ""
    assert result.display() == "US 14/123,456"
    assert str(result) == "US14123456"
