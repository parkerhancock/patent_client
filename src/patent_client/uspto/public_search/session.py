import hishel
import httpx

session = hishel.AsyncCacheClient(
    headers={
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    },
    transport=httpx.AsyncHTTPTransport(
        retries=3,
        verify=False,
        http2=True,
    ),
    timeout=5 * 60,
)
