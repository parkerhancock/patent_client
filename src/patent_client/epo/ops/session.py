import datetime as dt

from patent_client import SETTINGS
from patent_client.session import PatentClientSession

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


class OpsSession(PatentClientSession):
    def __init__(self, *args, key=None, secret=None, **kwargs):
        super(OpsSession, self).__init__(*args, **kwargs)
        self.key: str = key
        self.secret: str = secret
        self.expires: dt.datetime = dt.datetime.utcnow()

    def request(self, *args, **kwargs):
        response = super(OpsSession, self).request(*args, **kwargs)
        if response.status_code in (403, 400):
            auth_response = self.get_token()
            response = super(OpsSession, self).request(*args, **kwargs)
        return response

    def get_token(self):
        auth_url = "https://ops.epo.org/3.2/auth/accesstoken"
        with self.cache_disabled():
            response = super(OpsSession, self).request(
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


session = OpsSession(key=SETTINGS.EPO.API_KEY, secret=SETTINGS.EPO.API_SECRET)
