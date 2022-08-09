from patent_client.session import PatentClientSession


class FullTextException(Exception):
    pass


class FullTextSession(PatentClientSession):
    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)
        if "<TITLE>Error</TITLE>" in response.text:
            raise FullTextException(f"USPTO Returned an error!\n{response.text}")
        return response


session = FullTextSession()
