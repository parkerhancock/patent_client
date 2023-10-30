import asyncio

import pytest


@pytest.fixture(scope="module")
def vcr_config():
    return {
        # Replace the Authorization request header with "DUMMY" in cassettes
        "filter_headers": [("Authorization", "REDACTED")],
        # "serializer": "json",
        # "path_transformer": VCR.ensure_suffix(".json"),
        "record_mode": "new_episodes",
        "record_on_exception": False,
    }


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.vcr)
        # item.add_marker(pytest.mark.block_network)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
