import pytest
from pathlib import Path

from requests_cache.backends.sqlite import DbCache

import patent_client
#from .session import make_session

#test_db = Path(__file__).parent.parent.parent / "test_db.sqlite"

#test_session = make_session(db_path=test_db)

#@pytest.fixture(autouse=True)
def use_test_session():
    sess = patent_client.session
    patent_client.session = test_session
    yield 
    patent_client.session = sess