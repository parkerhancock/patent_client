import pytest

from patent_client import function_cache

function_cache.disable()


def pytest_collection_modifyitems(items):
    for item in items:
        if not item.get_closest_marker("no_vcr"):
            item.add_marker(pytest.mark.vcr)
        # item.add_marker(pytest.mark.block_network)


@pytest.fixture(params=[True, False], autouse=True, scope="package")
def cache(request):
    if request.param:
        function_cache.enable()
    else:
        function_cache.disable()
    yield
