from ..http_client import PatentClientAsyncHttpClient
from patent_client import function_cache


class GlobalDossierApi:
    http_client = PatentClientAsyncHttpClient(
        headers={
            "Authorization": "OQmPwAN1QD4OXe25jpmMD27zmnM21gIL0lg85G6j",
        }
    )

    @classmethod
    @function_cache
    async def get_dossier(cls, doc_number, type_code="application", office_code="US"):
        url = f"https://gd-api2.uspto.gov/patent-family/svc/family/{type_code}/{office_code}/{doc_number}"
        await cls.http_client.options(url)
        response = await cls.http_client.get(url)
        response.raise_for_status()
        return response.json()

    @classmethod
    @function_cache
    async def get_doc_list(cls, country, doc_number, kind_code):
        url = f"https://gd-api2.uspto.gov/doc-list/svc/doclist/{country}/{doc_number}/{kind_code}"
        response = await cls.http_client.get(url)
        response.raise_for_status()
        return response.json()

    @classmethod
    async def get_document(cls, country, doc_number, document_id, out_path):
        url = f"https://gd-api2.uspto.gov/doc-content/svc/doccontent/{country}/{doc_number}/{document_id}/1/PDF"
        return await cls.http_client.download(url, path=out_path)