import pytest

from patent_client import function_cache

function_cache.disable()


@pytest.fixture(params=[True, False], autouse=True, scope="session")
def cache(request):
    if request.param:
        function_cache.enable()
    else:
        function_cache.disable()
    yield
