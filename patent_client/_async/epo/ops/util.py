from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from pydantic import computed_field
from pydantic import model_validator
from yankee.xml.schema import Schema as XmlSchema

from patent_client.util.pydantic_util import BaseModel, async_proxy, AsyncProxy


if TYPE_CHECKING:
    from ..published.model import InpadocBiblio
    from ..published.model import Images
    from ..published.model import Claims
    from ..legal.model import LegalEvent
    from ..family.model import FamilyMember


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
    @computed_field
    @property
    def docdb_number(self) -> str:
        num = self.publication_reference_docdb
        if num.kind:
            return f"{num.country}{num.number}.{num.kind}"
        return f"{num.country}{num.number}"

    @property
    @async_proxy
    def biblio(self) -> "InpadocBiblio":
        return self._get_model(
            ".published.model.InpadocBiblio", base_class=InpadocModel
        ).objects.get(self.docdb_number)

    @property
    @async_proxy
    def images(self) -> "Images":
        return self._get_model(
            ".published.model.Images", base_class=InpadocModel
        ).objects.get(self.docdb_number)

    @property
    @async_proxy
    def description(self) -> Optional[str]:
        return AsyncProxy(
            self._get_model(
                ".published.model.Description", base_class=InpadocModel
            ).objects.get(self.docdb_number),
            attr="description",
        )

    @property
    @async_proxy
    def claims(self) -> "Claims":
        return self._get_model(
            ".published.model.Claims", base_class=InpadocModel
        ).objects.get(self.docdb_number)

    @property
    @async_proxy
    def legal(self) -> List["LegalEvent"]:
        return (
            self._get_model(".legal.model.Legal", base_class=InpadocModel)
            .objects.get(self.docdb_number)
            .events
        )

    @property
    @async_proxy
    def family(
        self,
    ) -> List["FamilyMember"]:
        return AsyncProxy(
            self._get_model(
                ".family.model.Family", base_class=InpadocModel
            ).objects.get(self.docdb_number),
            attr="family_members",
        )
