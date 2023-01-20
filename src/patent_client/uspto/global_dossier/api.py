from . import session


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
