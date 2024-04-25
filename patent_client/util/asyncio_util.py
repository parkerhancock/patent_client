import functools


class AsyncProxyObject:
    """
    Proxy for an async object that ensures the object is awaited and stored.
    """

    def __init__(self, coroutine, attr=None, index=None):
        self._coroutine = coroutine
        self._object = None
        self._attr = attr
        self._index = index

    async def _ensure_object(self):
        if self._object is None:
            self._object = await self._coroutine
        if self._index is not None:
            return self._object[self._index]
        elif self._attr is not None:
            return getattr(self._object, self._attr)
        return self._object

    def __getattr__(self, item):
        return AsyncProxyObject(self._ensure_object(), attr=item)

    def __getitem__(self, item):
        return AsyncProxyObject(self._ensure_object(), index=item)

    def __await__(self):
        return self._ensure_object().__await__()


def async_proxy(_func=None, *, attr=None):
    def decorator_async_proxy(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return AsyncProxyObject(func(*args, **kwargs), attr=attr)

        return wrapper

    if _func is None:
        return decorator_async_proxy
    else:
        return decorator_async_proxy(_func)
