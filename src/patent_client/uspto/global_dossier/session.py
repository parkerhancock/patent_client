import hishel
import httpx
from patent_client import __version__

session = hishel.AsyncCacheClient(
    headers={
        "Authorization": "OQmPwAN1QD4OXe25jpmMD27zmnM21gIL0lg85G6j",
        "User-Agent": f"Mozilla/5.0 Python Patent Clientbot/{__version__} (parkerhancock@users.noreply.github.com)",
    },
    transport=httpx.AsyncHTTPTransport(
        retries=3,
    ),
    timeout=5 * 60,
)
