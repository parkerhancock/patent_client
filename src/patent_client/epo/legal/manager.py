from patent_client.util import Manager

from .api import LegalApi


class LegalManager(Manager):
    def get(self, doc_number, doc_type="publication", format="docdb"):
        return LegalApi.get_legal(doc_number, doc_type, format).events
