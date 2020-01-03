import xml.etree.ElementTree as ET
from urllib import parse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests_cache

from patent_client import CACHE_CONFIG, CACHE_BASE, SETTINGS

CLIENT_SETTINGS = SETTINGS["ItcEdis"]
USERNAME = CLIENT_SETTINGS["Username"]
PASSWORD = CLIENT_SETTINGS["Password"]
key_file = CACHE_BASE / 'edis_key.txt'

class AuthenticationException(Exception):
    pass

class EdisSession(requests_cache.CachedSession):
    auth_url = "https://edis.usitc.gov/data/secretKey/"

    def __init__(self, *args, username, password, **kwargs):
        super(EdisSession, self).__init__(*args, **kwargs)
        self.username = username
        self.password = password
        self.secret_key = key_file.read_text() if key_file.exists() else ''
        self.auth = (self.username, self.secret_key)
        # Setup Retries
        retry = Retry(total=2, backoff_factor=0.2)
        self.mount('https://', HTTPAdapter(max_retries=retry))
        self.mount('http://', HTTPAdapter(max_retries=retry))

    def request(self, *args, **kwargs):
        response = super(EdisSession, self).request(*args, **kwargs)
        if not response.ok:
            self.authenticate()
            breakpoint()
            response = super(EdisSession, self).request(*args, **kwargs)
        return response

    def authenticate(self):
        with self.cache_disabled():
            response = super(EdisSession, self).request(
                "POST",
                f"{self.auth_url}{self.username}",
                params={"password": self.password}
                )
        import pdb; pdb.set_trace()
        if not response.ok:
            raise AuthenticationException(
                "EDIS Authentication Failed! Did you provide the correct username and password?"
            )
        tree = ET.fromstring(response.text)
        self.secret_key = tree.find("secretKey").text
        key_file.write_text(self.secret_key)
        self.auth = (self.username, self.secret_key)

session = EdisSession(username=USERNAME, password=PASSWORD, **CACHE_CONFIG)