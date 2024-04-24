from .model import DocumentList
from .model import GlobalDossier

from patent_client._async.http_client import PatentClientSession

client = PatentClientSession(
    headers={
        "Authorization": "OQmPwAN1QD4OXe25jpmMD27zmnM21gIL0lg85G6j",
    }
)


class GlobalDossierApi:
    async def get_file(self, doc_number, type_code="application", office_code="US"):
        url = f"https://gd-api2.uspto.gov/patent-family/svc/family/{type_code}/{office_code}/{doc_number}"
        pre_flight = await client.options(url)
        response = await client.get(url)
        response.raise_for_status()
        return GlobalDossier.model_validate_json(response.content)

    async def get_doc_list(self, country, doc_number, kind_code):
        url = f"https://gd-api2.uspto.gov/doc-list/svc/doclist/{country}/{doc_number}/{kind_code}"
        response = await client.get(url)
        response.raise_for_status()
        return DocumentList.model_validate_json(response.content)

    async def get_document(self, country, doc_number, document_id, out_path):
        url = f"https://gd-api2.uspto.gov/doc-content/svc/doccontent/{country}/{doc_number}/{document_id}/1/PDF"
        return await client.download(url, path=out_path)
