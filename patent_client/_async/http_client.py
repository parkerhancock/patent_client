import re
import typing as tp
import warnings
from hashlib import blake2b
from pathlib import Path

import hishel
import httpcore
import httpx
from hishel._utils import normalized_url

from patent_client import CACHE_DIR
from patent_client.version import __version__

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
        super().__init__(**kwargs)

    def get_filename(self, url, path, filename, headers):
        if path.is_dir() or None:
            try:
                filename = filename_re.search(headers["Content-Disposition"]).group(1)
            except (AttributeError, KeyError):
                filename = url.split("/")[-1]
            path = path / filename if path else Path.cwd() / filename
        return path

    async def download(
        self,
        url,
        method: str = "GET",
        path: tp.Optional[tp.Union[str, Path]] = None,
        **kwargs,
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
            path = self.get_filename(url, path, response, response.headers)
            with path.open("wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
        return path
