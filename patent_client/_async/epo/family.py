import lxml.etree as ET

from ..http_client import PatentClientAsyncHttpClient
from .auth import ops_auth
from patent_client import function_cache


class FamilyApi:
    http_client = PatentClientAsyncHttpClient(auth=ops_auth)

    @classmethod
    @function_cache
    async def get_family(cls, number, doc_type="publication", format="docdb"):
        url = f"http://ops.epo.org/3.2/rest-services/family/{doc_type}/{format}/{number}"
        response = await cls.http_client.get(url)
        return ET.fromstring(response.content)
