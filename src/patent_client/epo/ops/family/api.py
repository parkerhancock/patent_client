import lxml.etree as ET
from patent_client.epo.ops.session import session

from .schema import FamilySchema


class FamilyApi:
    schema = FamilySchema()

    @classmethod
    def get_family(cls, number, doc_type="publication", format="docdb"):
        url = f"http://ops.epo.org/3.2/rest-services/family/{doc_type}/{format}/{number}"
        response = session.get(url)
        response.raise_for_status()
        tree = ET.fromstring(response.text.encode())
        return cls.schema.load(tree)
