import re
import warnings
from pathlib import Path
from typing import Optional

import hishel
import httpx

from patent_client import CACHE_DIR
from patent_client.util.asyncio_util import run_sync
from patent_client.version import __version__

try:
    from IPython import get_ipython

    if "IPKernelApp" in get_ipython().config:
        from tqdm.notebook import tqdm
    else:
        from tqdm import tqdm
except (ImportError, AttributeError):
    from tqdm import tqdm

filename_re = re.compile(r'filename="([^"]+)"')


patent_client_transport = hishel.AsyncCacheTransport(
    transport=httpx.AsyncHTTPTransport(
        verify=False,
        http2=True,
        retries=3,
    ),
    storage=hishel.AsyncFileStorage(base_path=CACHE_DIR),
    controller=hishel.Controller(allow_heuristics=True),
)


class PatentClientSession(httpx.AsyncClient):
    _default_user_agent = f"Mozilla/5.0 Python Patent Clientbot/{__version__} (parkerhancock@users.noreply.github.com)"

    def __init__(self, **kwargs):
        kwargs["transport"] = kwargs.get("transport", patent_client_transport)
        headers = kwargs.get("headers", dict())
        headers["User-Agent"] = headers.get("User-Agent", self._default_user_agent)
        kwargs["headers"] = headers
        kwargs["follow_redirects"] = kwargs.get("follow_redirects", True)
        kwargs["timeout"] = kwargs.get("timeout", 60 * 5)
        super(PatentClientSession, self).__init__(**kwargs)

    def download(self, url, method: str = "GET", path: Optional[str | Path] = None, **kwargs):
        return run_sync(self.adownload(url, method, path, **kwargs))

    def get_filename(self, url, path, filename, headers):
        if path.is_dir() or None:
            try:
                filename = filename_re.search(headers["Content-Disposition"]).group(1)
            except (AttributeError, KeyError):
                filename = url.split("/")[-1]
            path = path / filename if path else Path.cwd() / filename
        return path

    async def adownload(
        self, url, method: str = "GET", path: Optional[str | Path] = None, show_progress: bool = False, **kwargs
    ):
        if isinstance(path, str):
            path = Path(path)
        elif path is None:
            path = Path.cwd()
        if not path.is_dir() and path.exists():
            warnings.warn(
                "File already exists at provided output! Not re-downloading. Please move the file or provide an alternative path to download"
            )
            return path
        async with self.stream(method, url, **kwargs) as response:
            response.raise_for_status()
            total = int(response.headers.get("Content-Length", 0)) or None
            with tqdm(total=total, unit_scale=True, unit_divisor=1024, unit="B", disable=not show_progress) as progress:
                num_bytes_downloaded = response.num_bytes_downloaded
                path = self.get_filename(url, path, response, response.headers)
                with path.open("wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
                        progress.update(response.num_bytes_downloaded - num_bytes_downloaded)
                        num_bytes_downloaded = response.num_bytes_downloaded
        return path
