from .model import NumberService
from patent_client._async.epo.number_service import NumberServiceApi as NumberServiceAsyncApi
from patent_client._sync.epo.number_service import NumberServiceApi as NumberServiceSyncApi
from patent_client.util.manager import Manager


class NumberServiceManager(Manager):
    async def aconvert_number(self, doc_number, doc_type="publication", input_format="original", output_format="docdb"):
        data = await NumberServiceAsyncApi.convert_number(doc_number, doc_type, input_format, output_format)
        return NumberService.model_validate(data)

    def convert_number(self, doc_number, doc_type="publication", input_format="original", output_format="docdb"):
        data = NumberServiceSyncApi.convert_number(doc_number, doc_type, input_format, output_format)
        return NumberService.model_validate(data)
