import pytest

from .family import FamilyApi

NS = {
    "http://ops.epo.org": None,
    "http://www.epo.org/exchange": None,
    "http://www.epo.org/fulltext": None,
    "http://www.epo.org/register": None,
}


@pytest.mark.anyio
async def test_api():
    result = await FamilyApi.get_family("EP1000000A1")
    count = int(result.find(".//{http://ops.epo.org}patent-family").attrib["total-result-count"])
    assert count >= 6
