import pytest
from patent_client import session as pc_session
from patent_client.epo.ops import session as epo_session


@pytest.fixture(autouse=True, scope="session")
def use_test_session():
    with pc_session.cache_disabled(), epo_session.cache_disabled():
        yield


@pytest.fixture(scope="module")
def vcr_config():
    return {
        # Replace the Authorization request header with "DUMMY" in cassettes
        "filter_headers": [("Authorization", "REDACTED")],
        # "serializer": "json",
        # "path_transformer": VCR.ensure_suffix(".json"),
        "record_mode": "new_episodes",
    }


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.vcr)
        # item.add_marker(pytest.mark.block_network)
