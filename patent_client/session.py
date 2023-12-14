import re
import warnings
from hashlib import blake2b
from pathlib import Path
from typing import Optional

import hishel
import httpcore
import httpx
from hishel._utils import normalized_url

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


def cache_key_generator(request: httpcore.Request):
    encoded_url = normalized_url(request.url).encode("ascii")
    body = [c for c in request.stream]
    if isinstance(body[0], bytes):
        body = b"".join(body)
    else:
        body = "".join(body).encode("utf-8")
    key = blake2b(digest_size=16)
    key.update(encoded_url)
    key.update(request.method)
    key.update(body)
    return key.hexdigest()


patent_client_transport = hishel.AsyncCacheTransport(
    transport=httpx.AsyncHTTPTransport(
        verify=False,
        http2=True,
        retries=3,
    ),
    storage=hishel.AsyncFileStorage(base_path=CACHE_DIR),
    controller=hishel.Controller(allow_heuristics=True, key_generator=cache_key_generator),
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
        # Ensure we skip the cache for file downloads
        kwargs["extensions"] = kwargs.get("extensions", dict())
        if "force_cache" in kwargs["extensions"]:
            raise ValueError("force_cache is not supported for file downloads")
        kwargs["extensions"]["cache_disabled"] = True
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
