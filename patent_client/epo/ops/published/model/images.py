from pathlib import Path
from typing import List
from typing import Optional

from pydantic import computed_field
from pydantic import Field
from pypdf import PdfReader
from pypdf import PdfWriter

from ..schema.images import ImageDocumentSchema
from ..schema.images import ImagesSchema
from patent_client._async.epo.published import PublishedImagesApi as PublishedImagesAsyncApi
from patent_client._sync.epo.published import PublishedImagesApi as PublishedImagesSyncApi
from patent_client.epo.ops.util import EpoBaseModel
from patent_client.epo.ops.util import InpadocModel


class Section(EpoBaseModel):
    name: Optional[str] = None
    start_page: Optional[int] = None


class ImageDocument(EpoBaseModel):
    __schema__ = ImageDocumentSchema()
    num_pages: Optional[int] = None
    description: Optional[str] = None
    link: Optional[str] = None
    formats: List[str] = Field(default_factory=list)
    sections: List[Section] = Field(default_factory=list)
    doc_number: Optional[str] = None

    def download(self, path="."):
        out_file = Path(path) / f"{self.doc_number}.pdf"
        writer = PdfWriter()
        for i in range(1, self.num_pages + 1):
            page_data = PublishedImagesSyncApi.get_page_image_from_link(self.link, page_number=i)
            page = PdfReader(page_data).pages[0]
            if page["/Rotate"] == 90:
                page.rotate_clockwise(-90)
            writer.add_page(page)

        for section in self.sections:
            writer.add_outline_item(section.name.capitalize(), section.start_page)

        with out_file.open("wb") as f:
            writer.write(f)

    async def adownload(self, path="."):
        out_file = Path(path) / f"{self.doc_number}.pdf"
        writer = PdfWriter()
        for i in range(1, self.num_pages + 1):
            page_data = await PublishedImagesAsyncApi.get_page_image_from_link(self.link, page_number=i)
            page = PdfReader(page_data).pages[0]
            if page["/Rotate"] == 90:
                page.rotate_clockwise(-90)
            writer.add_page(page)

        for section in self.sections:
            writer.add_outline_item(section.name.capitalize(), section.start_page)

        with out_file.open("wb") as f:
            writer.write(f)

    def download_image(self, path=".", image_format="tif", page_number=1):
        out_file = Path(path) / f"{self.doc_number}.{image_format}"

        image = PublishedImagesSyncApi.get_page_image_from_link(
            self.link, page_number=page_number, image_format=image_format
        )

        with out_file.open("wb") as f:
            f.write(image.read())

    async def adownload_image(self, path=".", image_format="tif", page_number=1):
        out_file = Path(path) / f"{self.doc_number}.{image_format}"

        image = await PublishedImagesAsyncApi.get_page_image_from_link(
            self.link, page_number=page_number, image_format=image_format
        )

        with out_file.open("wb") as f:
            f.write(image.read())


class Images(InpadocModel):
    __schema__ = ImagesSchema()
    publication_number: Optional[str] = None
    full_document: Optional[ImageDocument] = None
    drawing: Optional[ImageDocument] = None
    first_page: Optional[ImageDocument] = None

    @computed_field
    @property
    def docdb_number(self) -> str:
        return str(self.publication_number)
