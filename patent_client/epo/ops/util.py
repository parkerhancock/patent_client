from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from pydantic import model_validator
from yankee.xml.schema import Schema as XmlSchema

from patent_client.util.pydantic_util import BaseModel
from patent_client.util.related import get_model

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


class EpoBaseModel(BaseModel):
    __schema__: Optional[XmlSchema] = None

    @model_validator(mode="before")
    @classmethod
    def xml_convert(cls, values):
        if isinstance(values, (str, bytes)):
            return cls.__schema__.load(values).to_dict()
        return values


class InpadocModel(EpoBaseModel):
    @property
    def biblio(self) -> "InpadocBiblio":
        return get_model("patent_client.epo.ops.published.model.InpadocBiblio").objects.get(self.docdb_number)

    @property
    def images(self) -> "Images":
        return get_model("patent_client.epo.ops.published.model.Images").objects.get(self.docdb_number)

    @property
    def description(self) -> Optional[str]:
        return get_model("patent_client.epo.ops.published.model.Description").objects.get(self.docdb_number).description

    @property
    def claims(self) -> "Claims":
        return get_model("patent_client.epo.ops.published.model.Claims").objects.get(self.docdb_number)

    @property
    def legal(self) -> List["LegalEvent"]:
        return get_model("patent_client.epo.ops.legal.model.Legal").objects.get(self.docdb_number).events

    @property
    def family(
        self,
    ) -> List["FamilyMember"]:
        return get_model("patent_client.epo.ops.family.model.Family").objects.get(self.docdb_number).family_members
