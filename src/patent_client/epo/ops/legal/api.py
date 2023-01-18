from patent_client.epo.ops.session import session


class LegalApi:
    @classmethod
    def get_legal(cls, doc_number, doc_type="publication", format="docdb"):
        url = f"http://ops.epo.org/3.2/rest-services/legal/{doc_type}/{format}/{doc_number}"
        response = session.get(url)
        response.raise_for_status()
        return response.text
