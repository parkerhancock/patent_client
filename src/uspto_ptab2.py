import requests

session = requests.Session()


class PtabManager:
    def __init__(self, config=dict()):
        self.config = config

    def filter(self, **kwargs):
        return self.__class__({**self.config, **kwargs})

    def get(self, **kwargs):
        manager = self.filter(**kwargs)
        if len(manager) > 1:
            raise ValueError("More than 1 record matched!")
        return manager.first()

    def first(self):
        return next(self)

    def __iter__(self):
        url = "https://developer.uspto.gov/ptab-api/proceedings"
        offset = self.config.get("offset", 0)
        limit = self.config.get("limit", None) or len(self) - offset
