from httpx._exceptions import HTTPStatusError

from patent_client.session import PatentClientSession


class NotAvailableException(Exception):
    pass


class PEDSSession(PatentClientSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_hooks["response"].append(self.handle_peds_down_exception)

    async def is_online(self) -> bool:
        with session.cache_disabled():
            response = await session.get("https://ped.uspto.gov/api/search-fields")
            if response.status_code == 200:
                return True
            else:
                self._read_error(response)

    def _read_error(self, response):
        if "requested resource is not available" in response.text:
            raise NotAvailableException("Patent Examination Data is Offline - this is a USPTO problem")
        elif "attempt failed or the origin closed the connection" in response.text:
            raise NotAvailableException("The Patent Examination Data API is Broken! - this is a USPTO problem")
        else:
            raise NotAvailableException("There is a USPTO problem")

    def handle_peds_down_exception(self, response):
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            response.read()
            self._read_error(response)


session = PEDSSession()
