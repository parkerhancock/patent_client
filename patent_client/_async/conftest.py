import asyncio

import pytest

"""
@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope="session")
def event_loop(request):
    #Redefine the event loop to support session/module-scoped fixtures;
    #see https://github.com/pytest-dev/pytest-asyncio/issues/68
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    try:
        yield loop
    finally:
        loop.close()
"""
