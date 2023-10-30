import asyncio


def run_sync(coroutine):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        return asyncio.run(coroutine)
    else:
        return loop.run_until_complete(coroutine)


def run_async_iterator(async_iterator):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    while True:
        try:
            yield loop.run_until_complete(async_iterator.__anext__())
        except StopAsyncIteration:
            break
