import re
import warnings
from pathlib import Path
from typing import Optional

import httpx

from patent_client import __version__


filename_re = re.compile(r'filename="([^"]+)"')


class PatentClientAsyncHttpClient(httpx.AsyncClient):
    _default_user_agent = f"Mozilla/5.0 Python Patent Clientbot/{__version__} (parkerhancock@users.noreply.github.com)"

    def __init__(self, **kwargs):
        headers = kwargs.get("headers", dict())
        headers["User-Agent"] = headers.get("User-Agent", self._default_user_agent)
        kwargs["headers"] = headers
        kwargs["follow_redirects"] = kwargs.get("follow_redirects", True)
        kwargs["timeout"] = kwargs.get("timeout", 60 * 5)
        kwargs["verify"] = kwargs.get("verify", False)
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
        path: Optional[str | Path] = None,
        show_progress: bool = False,
        **kwargs,
    ):
        # Ensure we skip the cache for file downloads
        kwargs["extensions"] = kwargs.get("extensions", dict())
        if "force_cache" in kwargs["extensions"]:
            raise ValueError("force_cache is not supported for file downloads")
        kwargs["extensions"]["cache_disabled"] = True
        if isinstance(path, str):
            base_path = Path(path)
        elif path is None:
            base_path = Path.cwd()
        else:
            base_path = path
        if not base_path.is_dir() and base_path.exists():
            warnings.warn(
                "File already exists at provided output! Not re-downloading. Please move the file or provide an alternative path to download"
            )
            return base_path
        async with self.stream(method, url, **kwargs) as response:
            response.raise_for_status()
            out_path = self.get_filename(url, base_path, response, response.headers)
            with out_path.open("wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
        return path