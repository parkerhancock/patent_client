import pytest
from unittest.mock import AsyncMock
from .pydantic_util import AsyncProxy


@pytest.mark.asyncio
async def test_async_proxy_getattr():
    # Mocking an async function that returns a value
    async def mock_coroutine():
        return {"key": "value"}

    proxy = AsyncProxy(mock_coroutine())
    assert (
        await proxy.key == "value"
    ), "AsyncProxy did not correctly get attribute from async object"


@pytest.mark.asyncio
async def test_async_proxy_await():
    # Mocking an async function that returns a value
    async def mock_coroutine():
        return "awaited result"

    proxy = AsyncProxy(mock_coroutine())
    assert (
        await proxy == "awaited result"
    ), "AsyncProxy did not correctly await the coroutine"


@pytest.mark.asyncio
async def test_async_proxy_ensure_object():
    # Mocking an async function that returns a value
    async def mock_coroutine():
        return "ensured object"

    proxy = AsyncProxy(mock_coroutine())
    await proxy._ensure_object()  # Directly testing the private method
    assert (
        proxy._object == "ensured object"
    ), "AsyncProxy did not correctly ensure object is awaited and stored"


@pytest.mark.asyncio
async def test_async_proxy_getattr_not_existing():
    # Mocking an async function that returns a value
    async def mock_coroutine():
        return {"key": "value"}

    proxy = AsyncProxy(mock_coroutine())
    with pytest.raises(AttributeError):
        await proxy.non_existing_attribute
