from patent_client.util import Manager

from .api import LegalApi
from .schema import LegalSchema


class LegalManager(Manager):
    __schema__ = LegalSchema

    def get(self, doc_number, doc_type="publication", format="docdb"):
        return self.__schema__.load(LegalApi.get_legal(doc_number, doc_type, format)).events
