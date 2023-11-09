import datetime as dt
from typing import Optional

from patent_client import SETTINGS
from patent_client.session import PatentClientSession
from patent_client.util.asyncio_util import SyncProxy

NS = {
    "http://ops.epo.org": None,
    "http://www.epo.org/exchange": None,
    "http://www.epo.org/fulltext": None,
    "http://www.epo.org/register": None,
}

import logging

logger = logging.getLogger(__name__)


class OpsAuthenticationError(Exception):
    pass


class OpsForbiddenError(Exception):
    pass


class OpsFairUseError(Exception):
    pass


class OpsAsyncSession(PatentClientSession):
    key: Optional[str]
    secret: Optional[str]
    expires: dt.datetime
    sync: SyncProxy

    def __init__(self, *args, key: Optional[str] = None, secret: Optional[str] = None, **kwargs):
        super(OpsAsyncSession, self).__init__(*args, **kwargs)
        self.key = key
        self.secret = secret
        self.expires = dt.datetime.utcnow()
        self.sync = SyncProxy(self)

    async def request(self, *args, **kwargs):
        response = await super(OpsAsyncSession, self).request(*args, **kwargs)
        if response.status_code in (403, 400):
            auth_response = await self.get_token()
            response = await super(OpsAsyncSession, self).request(*args, **kwargs)
        if response.status_code in (403, 400):
            if "Fair Use policy" in response.text:
                raise OpsFairUseError(f"EPO Fair Use Policy Error!\n{response.text}{response.headers}")
            else:
                raise OpsForbiddenError(f"EPO Request Error!\nStatus Code: {response.status_code}\n{response.text}")
        response.raise_for_status()
        return response

    async def get_token(self):
        auth_url = "https://ops.epo.org/3.2/auth/accesstoken"
        response = await super(OpsAsyncSession, self).request(
            "post",
            auth_url,
            auth=(self.key, self.secret),
            data={"grant_type": "client_credentials"},
        )
        if response.status_code == 401:
            logger.debug(f"EPO Authentication Error!\n{response.text}")
            raise OpsAuthenticationError(
                "Failed to authenticate with EPO OPS! Please check your credentials. See the setup instructions at https://patent-client.readthedocs.io/en/stable/getting_started.html"
            )
        elif response.status_code == 403:
            logger.debug(f"EPO Forbidden Error\n{response.text}")
            raise OpsForbiddenError("Your EPO Request Failed - Quota Exceeded / Blacklisted / Blocked")
        response.raise_for_status()

        data = response.json()
        self.expires = dt.datetime.fromtimestamp(int(data["issued_at"]) / 1000) + dt.timedelta(
            seconds=int(data["expires_in"])
        )
        self.headers["Authorization"] = f"Bearer {data['access_token']}"
        return response


asession = OpsAsyncSession(key=SETTINGS.epo_api_key, secret=SETTINGS.epo_api_secret)
