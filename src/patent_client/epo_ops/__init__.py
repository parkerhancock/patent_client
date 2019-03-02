from patent_client import CACHE_BASE, TEST_BASE

CACHE_DIR = CACHE_BASE / "epo"
CACHE_DIR.mkdir(exist_ok=True)
TEST_DIR = TEST_BASE / "epo"
TEST_DIR.mkdir(exist_ok=True)
