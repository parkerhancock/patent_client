import pytest
from httpx import MockTransport
from httpx import Response

from .session import NotAvailableException
from .session import session


@pytest.mark.asyncio
async def test_peds_is_down_response():
    def handler(request):
        return Response(504, request=request)

    session._transport = MockTransport(handler)
    with pytest.raises(NotAvailableException):
        await session.get("https://ped.uspto.gov/api/search-fields")
