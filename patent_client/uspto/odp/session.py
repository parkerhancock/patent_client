import httpx
from patent_client import SETTINGS

client = httpx.Client(
    follow_redirects=True,
    headers={"X-API-KEY": SETTINGS.odp_api_key},
)

