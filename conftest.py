import asyncio
import inspect
from pathlib import Path

import pytest

collect_ignore = [
    "hishel",
]


@pytest.fixture(scope="session")
def load_dotenv():
    import dotenv

    dotenv.load_dotenv()


def path_generator_function(function):
    func_path = inspect.getfile(function)
    func_path = func_path.replace("_async/", "")
    func_path = func_path.replace("_sync/", "")
    return str(Path(func_path) / function.__name__)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        # Replace the Authorization request header with "REDACTED" in cassettes
        "filter_headers": [("Authorization", "REDACTED")],
        # "serializer": "json",
        # "path_transformer": VCR.ensure_suffix(".json"),
        "record_mode": "new_episodes",
        "record_on_exception": False,
        "func_path_generator": path_generator_function,
    }


def pytest_collection_modifyitems(items):
    for item in items:
        if not item.get_closest_marker("no_vcr"):
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
