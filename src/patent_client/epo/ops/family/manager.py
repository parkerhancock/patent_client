from patent_client.util import Manager

from .api import FamilyApi
from .schema import FamilySchema


class FamilyManager(Manager):
    __schema__ = FamilySchema

    def get(self, doc_number):
        return self.__schema__.load(FamilyApi.get_family(doc_number, doc_type="publication", format="docdb"))
