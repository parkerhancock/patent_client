from .model import Family
from patent_client._async.epo.family import FamilyApi as FamilyAsyncApi
from patent_client._sync.epo.family import FamilyApi as FamilySyncApi
from patent_client.util.manager import Manager


class FamilyManager(Manager[Family]):
    async def aget(self, doc_number):
        tree = await FamilyAsyncApi.get_family(doc_number, doc_type="publication", format="docdb")
        return Family.model_validate(tree)

    def get(self, doc_number):
        tree = FamilySyncApi.get_family(doc_number, doc_type="publication", format="docdb")
        return Family.model_validate(tree)
