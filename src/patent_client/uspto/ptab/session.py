from pathlib import Path

from patent_client.session import PatentClientSession


class PtabSession(PatentClientSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verify = str(Path(__file__).parent / "developer.uspto.gov.crt")
