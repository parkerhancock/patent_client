import datetime
import requests_cache
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from patent_client import SETTINGS
from patent_client.version import __version__

CACHE_CONFIG = dict(
            expire_after=SETTINGS.CACHE.MAX_AGE,
            db_path=Path(SETTINGS.DEFAULT.BASE_DIR) / SETTINGS.CACHE.PATH,
            backend="sqlite",
            allowable_methods=("GET", "POST"),
            ignored_parameters=[
                "Authorization",
            ],
        )


class PatentClientSession(requests_cache.CachedSession):
    def __init__(self):
        super().__init__(**CACHE_CONFIG)
        self.remove_expired_responses(expire_after=SETTINGS.CACHE.MAX_AGE)
        self.headers["User-Agent"] = f"Python Patent Clientbot/{__version__} (parkerhancock@users.noreply.github.com)"
        # Install a default retry on the session using urrlib3
        retry = Retry(total=5, backoff_factor=0.2)
        self.mount("https://", HTTPAdapter(max_retries=retry))
        self.mount("http://", HTTPAdapter(max_retries=retry))