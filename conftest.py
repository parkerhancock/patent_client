import asyncio
import inspect
import os
from pathlib import Path

import pytest
import vcr

os.environ.setdefault("PATENT_CLIENT_ODP_API_KEY", "vcr-placeholder")

collect_ignore = [
    "hishel",
]


@pytest.fixture(scope="session")
def load_dotenv():
    import dotenv

    dotenv.load_dotenv()


ROOT_DIR = Path(__file__).parent.resolve()


def path_generator_function(function):
    func_path = Path(inspect.getfile(function))
    if func_path.is_absolute():
        try:
            func_path = func_path.relative_to(ROOT_DIR)
        except ValueError:
            func_path = func_path.name
    func_str = str(func_path).replace("_async/", "").replace("_sync/", "")
    return str(Path(func_str) / function.__name__)


CASSETTE_ROOT = Path("cassettes")
_vcr = vcr.VCR(
    cassette_library_dir=str(CASSETTE_ROOT),
    record_mode="once",
    record_on_exception=False,
    filter_headers=[("Authorization", "REDACTED"), ("X-API-KEY", "REDACTED")],
)


def pytest_collection_modifyitems(items):
    for item in items:
        if not item.get_closest_marker("no_vcr"):
            item.add_marker(pytest.mark.vcr)
        # item.add_marker(pytest.mark.block_network)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    marker = item.get_closest_marker("vcr")
    if not marker:
        yield
        return

    cassette_name = path_generator_function(item.function) + ".yaml"
    cassette_path = CASSETTE_ROOT / cassette_name
    cassette_path.parent.mkdir(parents=True, exist_ok=True)

    with _vcr.use_cassette(str(cassette_path)):
        yield


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
