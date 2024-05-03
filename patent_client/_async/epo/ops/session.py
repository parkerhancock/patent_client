import base64
import datetime as dt
import logging
from typing import Sequence

import hishel
import httpx
from httpcore import Request, Response

from patent_client import SETTINGS
from patent_client._async.http_client import PatentClientSession
from patent_client.session import CACHE_DIR

logger = logging.getLogger(__name__)

NS = {
    "http://ops.epo.org": None,
    "http://www.epo.org/exchange": None,
    "http://www.epo.org/fulltext": None,
    "http://www.epo.org/register": None,
}


class OpsAuthenticationError(Exception):
    pass


class OpsForbiddenError(Exception):
    pass


class OpsFairUseError(Exception):
    pass


class OpsController(hishel.Controller):
    def __init__(
        self,
        cacheable_methods: Sequence[str] = ("GET", "HEAD"),
        cacheable_status_codes: Sequence[int] = (200,),
    ):
        super().__init__()
        self.cacheable_methods = cacheable_methods
        self.cacheable_status_codes = cacheable_status_codes

    def is_cachable(self, request: Request, response: Response) -> bool:
        return (
            request.method in self.cacheable_methods
            and response.status_code in self.cacheable_status_codes
        )

    def construct_response_from_cache(self, request, response, original_request):
        return response


class OpsAuth(httpx.Auth):
    requires_response_body = True
    auth_url = "https://ops.epo.org/3.2/auth/accesstoken"

    def __init__(self, key: str, secret: str):
        self.key = key
        self.secret = secret
        self.authorization_header = "<unset>"

    def auth_flow(self, request):
        request.headers["Authorization"] = self.authorization_header
        response = yield request

        if response.status_code == 400:
            response = yield self.build_refresh_request()
            if response.status_code != 200:
                logger.debug(f"EPO Authentication Error!\n{response.text}")
                raise OpsAuthenticationError(
                    "Failed to authenticate with EPO OPS! Please check your credentials. See the setup instructions at https://patent-client.readthedocs.io/en/stable/getting_started.html"
                )
            data = response.json()
            self.expires = dt.datetime.fromtimestamp(int(data["issued_at"]) / 1000) + dt.timedelta(
                seconds=int(data["expires_in"])
            )
            self.authorization_header = f"Bearer {data['access_token']}"
            request.headers["Authorization"] = self.authorization_header
            yield request

    def build_refresh_request(self):
        token = base64.b64encode(f"{self.key}:{self.secret}".encode())
        return httpx.Request(
            "post",
            self.auth_url,
            headers={"Authorization": token},
            data={"grant_type": "client_credentials"},
        )


ops_transport = hishel.AsyncCacheTransport(
    transport=httpx.AsyncHTTPTransport(
        verify=False,
        http2=True,
        retries=3,
    ),
    storage=hishel.AsyncFileStorage(base_path=CACHE_DIR, ttl=60 * 60 * 24 * 3),
    controller=OpsController(),
)


async def handle_response(response):
    if response.status_code == 403:
        raise OpsForbiddenError("Forbidden")
    return response


session = PatentClientSession(
    transport=ops_transport,
    auth=OpsAuth(key=SETTINGS.epo_api_key, secret=SETTINGS.epo_api_secret),
    event_hooks={
        "response": [
            handle_response,
        ]
    },
)
