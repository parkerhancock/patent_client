import re

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        if not item.get_closest_marker("no_vcr"):
            item.add_marker(pytest.mark.vcr)
        # item.add_marker(pytest.mark.block_network)


bracket_re = re.compile(r"\[(.*?)\]")


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "REDACTED")],
        "record_mode": "new_episodes",
        "record_on_exception": False,
        "path_transformer": lambda path: bracket_re.sub(r"", path) + ".yaml",
    }
