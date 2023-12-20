import asyncio


def run_sync(coroutine):
    import nest_asyncio

    nest_asyncio.apply()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    return loop.run_until_complete(coroutine)


def run_async_iterator(async_iterator):
    while True:
        try:
            yield run_sync(async_iterator.__anext__())
        except StopAsyncIteration:
            break


def run_sync_decorator(func):
    def wrapper(*args, **kwargs):
        return run_sync(func(*args, **kwargs))

    return wrapper


def run_sync_iterator_decorator(func):
    def wrapper(*args, **kwargs):
        return run_async_iterator(func(*args, **kwargs))

    return wrapper


class SyncProxy:
    def __init__(self, async_obj):
        self.async_obj = async_obj

    def __getattr__(self, name):
        return run_sync_decorator(getattr(self.async_obj, name))

    def __iter__(self):
        return run_sync_iterator_decorator(self.async_obj.__aiter__())
