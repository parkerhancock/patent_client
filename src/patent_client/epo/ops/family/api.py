from patent_client.epo.ops.session import asession


class FamilyAsyncApi:
    @classmethod
    async def get_family(cls, number, doc_type="publication", format="docdb"):
        url = f"http://ops.epo.org/3.2/rest-services/family/{doc_type}/{format}/{number}"
        response = await asession.get(url)
        response.raise_for_status()
        return response.text
