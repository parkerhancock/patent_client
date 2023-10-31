import hishel
import httpx

session = hishel.AsyncCacheClient(
    transport=httpx.AsyncHTTPTransport(
        retries=3,
        verify=False,
    ),
    timeout=60 * 5,
)
