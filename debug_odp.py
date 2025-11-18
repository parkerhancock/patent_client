import os
import httpx
from patent_client.settings import Settings

settings = Settings()
api_key = os.environ.get("PATENT_CLIENT_ODP_API_KEY")

if not api_key:
    print("API Key not found!")
    exit(1)

url = "https://api.uspto.gov/api/v1/patent/applications/16123456"
headers = {"X-API-KEY": api_key}

print(f"Requesting {url}...")
response = httpx.get(url, headers=headers)
print(f"Status: {response.status_code}")
try:
    print(response.json())
except Exception as e:
    print(f"Error parsing JSON: {e}")
    print(response.text)
