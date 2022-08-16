import re
from urllib.parse import urljoin
import time
from patent_client.session import PatentClientSession

redirect_re = re.compile(r'(?P<wait>\d+);URL=(?P<redirect_url>[^"]+)')

class FullTextException(Exception):
    pass


class FullTextSession(PatentClientSession):
    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        if "<TITLE>Error</TITLE>" in response.text:
            raise FullTextException(f"USPTO Returned an error!\n{response.text}")
        match = redirect_re.search(response.text)
        if match:
            path = match.groupdict()['redirect_url']
            path = path.replace("&gt;", "%3E") # PTO doesn't accept new-style XML entities
            wait = int(match.groupdict()['wait'])
            time.sleep(wait)
            new_response = super().get(urljoin(response.url, path))
            return new_response
        return response


session = FullTextSession()
