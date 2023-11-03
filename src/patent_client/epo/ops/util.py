from typing import Optional
from typing import TYPE_CHECKING

from patent_client.util import Model
from patent_client.util.base.related import get_model
from yankee.data import ListCollection
from yankee.xml.schema import Schema as XmlSchema

if TYPE_CHECKING:
    from patent_client.epo.ops.published.model import InpadocBiblio
    from patent_client.epo.ops.published.model import Images
    from patent_client.epo.ops.published.model import Claims
    from patent_client.epo.ops.legal.model import LegalEvent
    from patent_client.epo.ops.family.model import FamilyMember


class Schema(XmlSchema):
    class Meta:
        namespaces = {
            "ops": "http://ops.epo.org",
            "epo": "http://www.epo.org/exchange",
            "ft": "http://www.epo.org/fulltext",
        }


class InpadocModel(Model):
    @property
    def biblio(self) -> "InpadocBiblio":
        return get_model("patent_client.epo.ops.published.model.InpadocBiblio").objects.get(self.docdb_number)

    @property
    def images(self) -> "Images":
        return get_model("patent_client.epo.ops.published.model.Images").objects.get(self.docdb_number)

    @property
    def description(self) -> Optional[str]:
        return get_model("Description").objects.get(self.docdb_number).description

    @property
    def claims(self) -> "Claims":
        return get_model("patent_client.epo.ops.published.model.Claims").objects.get(self.docdb_number)

    @property
    def legal(self) -> "ListCollection[LegalEvent]":
        return get_model("patent_client.epo.ops.legal.model.Legal").objects.get(self.docdb_number).events

    @property
    def family(
        self,
    ) -> "ListCollection[FamilyMember]":
        return get_model("patent_client.epo.ops.family.model.Family").objects.get(self.docdb_number).family_members
