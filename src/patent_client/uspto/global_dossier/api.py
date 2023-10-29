import httpx

from . import session

asession = httpx.AsyncClient(headers={"Authorization": "OQmPwAN1QD4OXe25jpmMD27zmnM21gIL0lg85G6j"})


class GlobalDossierApi:
    def get_file(self, doc_number, type_code="application", office_code="US"):
        url = f"https://gd-api2.uspto.gov/patent-family/svc/family/{type_code}/{office_code}/{doc_number}"
        pre_flight = session.options(url)
        response = session.get(url)
        response.raise_for_status()
        return response.json()

    def get_doc_list(self, country, doc_number, kind_code):
        url = f"https://gd-api2.uspto.gov/doc-list/svc/doclist/{country}/{doc_number}/{kind_code}"
        response = session.get(url)
        response.raise_for_status()
        return response.json()

    def get_document(self, country, doc_number, document_id, out_path):
        if out_path.exists():
            return out_path

        url = f"https://gd-api2.uspto.gov/doc-content/svc/doccontent/{country}/{doc_number}/{document_id}/1/PDF"
        response = session.get(url, stream=True)
        response.raise_for_status()
        with out_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return out_path


class GlobalDossierAsyncApi:
    async def get_file(self, doc_number, type_code="application", office_code="US"):
        url = f"https://gd-api2.uspto.gov/patent-family/svc/family/{type_code}/{office_code}/{doc_number}"
        pre_flight = await asession.options(url)
        response = await asession.get(url)
        response.raise_for_status()
        return response.json()

    async def get_doc_list(self, country, doc_number, kind_code):
        url = f"https://gd-api2.uspto.gov/doc-list/svc/doclist/{country}/{doc_number}/{kind_code}"
        response = await asession.get(url)
        response.raise_for_status()
        return response.json()

    async def get_document(self, country, doc_number, document_id, out_path):
        if out_path.exists():
            return out_path

        url = f"https://gd-api2.uspto.gov/doc-content/svc/doccontent/{country}/{doc_number}/{document_id}/1/PDF"
        async with session.stream(url, stream=True) as response:
            response.raise_for_status()
            with out_path.open("wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return out_path
