from ..session import session
from .model import Family


class FamilyAsyncApi:
    @classmethod
    async def get_family(cls, number, doc_type="publication", format="docdb"):
        url = f"http://ops.epo.org/3.2/rest-services/family/{doc_type}/{format}/{number}"
        response = await session.get(url)
        return Family.model_validate(response.text)
