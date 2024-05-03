from typing import TYPE_CHECKING, List, Optional

from async_property import async_property
from async_property.base import AsyncPropertyDescriptor
from pydantic import ConfigDict, computed_field, model_validator
from yankee.xml.schema import Schema as XmlSchema

from patent_client.util.pydantic_util import BaseModel

if TYPE_CHECKING:
    from .family.model import FamilyMember
    from .legal.model import LegalEvent
    from .published.model import Claims, Images, InpadocBiblio


class Schema(XmlSchema):
    class Meta:
        namespaces = {
            "ops": "http://ops.epo.org",
            "epo": "http://www.epo.org/exchange",
            "ft": "http://www.epo.org/fulltext",
        }


class EpoBaseModel(BaseModel):
    model_config = ConfigDict(ignored_types=(AsyncPropertyDescriptor,))
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

    @async_property
    async def biblio(self) -> "InpadocBiblio":
        return await self._get_model(
            ".published.model.InpadocBiblio", base_class=InpadocModel
        ).objects.get(self.docdb_number)

    @async_property
    async def images(self) -> "Images":
        return await self._get_model(
            ".published.model.Images", base_class=InpadocModel
        ).objects.get(self.docdb_number)

    @async_property
    async def description(self) -> Optional[str]:
        return (
            await self._get_model(
                ".published.model.Description", base_class=InpadocModel
            ).objects.get(self.docdb_number)
        ).description

    @async_property
    async def claims(self) -> "Claims":
        return await self._get_model(
            ".published.model.Claims", base_class=InpadocModel
        ).objects.get(self.docdb_number)

    @async_property
    async def legal(self) -> List["LegalEvent"]:
        return (
            await self._get_model(".legal.model.Legal", base_class=InpadocModel).objects.get(
                self.docdb_number
            )
        ).events

    @async_property
    async def family(
        self,
    ) -> List["FamilyMember"]:
        return (
            await self._get_model(".family.model.Family", base_class=InpadocModel).objects.get(
                self.docdb_number
            )
        ).family_members

    async def download(self, path: str = "."):
        images = await self.images
        return await images.full_document.download(path)
