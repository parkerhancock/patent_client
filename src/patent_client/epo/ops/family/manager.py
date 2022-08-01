from patent_client.util import Manager

from .api import FamilyApi

class FamilyManager(Manager):
    def get(self, doc_number):
        return FamilyApi.get_family(doc_number, doc_type="publication", format="docdb")
