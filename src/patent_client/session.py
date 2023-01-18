from pathlib import Path

import requests_cache
from patent_client import SETTINGS
from patent_client.version import __version__
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class PatentClientSession(requests_cache.CachedSession):
    def __init__(self):
        super().__init__(
            Path(SETTINGS.DEFAULT.BASE_DIR).expanduser() / SETTINGS.CACHE.PATH,
            expire_after=SETTINGS.CACHE.MAX_AGE,
            backend="sqlite",
            allowable_methods=("GET", "POST"),
            ignored_parameters=[
                "Authorization",
            ],
        )
        self.headers["User-Agent"] = f"Python Patent Clientbot/{__version__} (parkerhancock@users.noreply.github.com)"
        # Install a default retry on the session using urrlib3
        retry = Retry(total=5, backoff_factor=0.2)
        self.mount("https://", HTTPAdapter(max_retries=retry))
        self.mount("http://", HTTPAdapter(max_retries=retry))
