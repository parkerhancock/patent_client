from httpx import Client


class PublicSearchClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["X-Requested-With"] = "XMLHttpRequest"
        self.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"


client = PublicSearchClient(http2=True)
