from ..session import session
from .model import Legal


class LegalApi:
    @classmethod
    async def get_legal(cls, doc_number, doc_type="publication", format="docdb"):
        url = f"http://ops.epo.org/3.2/rest-services/legal/{doc_type}/{format}/{doc_number}"
        response = await session.get(url)

        return Legal.model_validate(response.text)
