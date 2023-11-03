import re
from pathlib import Path
from typing import Optional

import hishel
import httpx
from patent_client import CACHE_DIR
from patent_client.util.asyncio_util import run_sync
from patent_client.version import __version__

filename_re = re.compile(r'filename="([^"]+)"')


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
        kwargs["timeout"] = kwargs.get("timeout", self._default_timeout)
        super(PatentClientSession, self).__init__(**kwargs)

    def download(self, url, method: str = "GET", path: Optional[str | Path] = None, **kwargs):
        return run_sync(self.adownload(url, method, path, **kwargs))

    async def adownload(self, url, method: str = "GET", path: Optional[str | Path] = None, **kwargs):
        if isinstance(path, str):
            path = Path(path)
        async with self.stream(method, url, **kwargs) as response:
            response.raise_for_status()
            if path.is_dir() or None:
                filename = filename_re.search(response.headers["Content-Disposition"]).group(1)
                path = path / filename if path else Path.cwd() / filename
            with path.open("wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
        return path
