import hishel
import httpx
from patent_client import CACHE_DIR
from patent_client.version import __version__


class PatentClientSession(hishel.AsyncCacheClient):
    _default_transport = httpx.AsyncHTTPTransport(
        retries=3,
        verify=False,
        http2=True,
    )
    _default_timeout = 60 * 5
    _default_user_agent = f"Mozilla/5.0 Python Patent Clientbot/{__version__} (parkerhancock@users.noreply.github.com)"
    _default_storage = hishel.AsyncFileStorage(base_path=CACHE_DIR)
    _default_controller = hishel.Controller(
        allow_heuristics=True,
    )

    def __init__(self, **kwargs):
        kwargs["transport"] = kwargs.get("transport", self._default_transport)
        kwargs["storage"] = kwargs.get("storage", self._default_storage)
        kwargs["controller"] = kwargs.get("controller", self._default_controller)
        headers = kwargs.get("headers", dict())
        headers["User-Agent"] = headers.get("User-Agent", self._default_user_agent)
        kwargs["headers"] = headers
        kwargs["follow_redirects"] = kwargs.get("follow_redirects", True)
        super(PatentClientSession, self).__init__(**kwargs)
