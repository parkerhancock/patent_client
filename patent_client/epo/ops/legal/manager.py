from yankee.data import ListCollection

from .model import Legal
from .model import LegalEvent
from patent_client._async.epo.legal import LegalApi as LegalAsyncApi
from patent_client._sync.epo.legal import LegalApi as LegalSyncApi
from patent_client.util.manager import Manager


class LegalManager(Manager):
    async def aget(self, doc_number, doc_type="publication", format="docdb") -> ListCollection[LegalEvent]:
        data = await LegalAsyncApi.get_legal(doc_number, doc_type, format)
        return Legal().model_validate(data).events

    def get(self, doc_number, doc_type="publication", format="docdb") -> ListCollection[LegalEvent]:
        data = LegalSyncApi.get_legal(doc_number, doc_type, format)
        return Legal().model_validate(data).events
