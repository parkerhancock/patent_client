from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import List

from patent_client.epo.ops.util import InpadocModel
from patent_client.util import Model
from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter


@dataclass
class Section(Model):
    name: str = None
    start_page: int = None


@dataclass
class ImageDocument(Model):
    num_pages: int = None
    description: str = None
    link: str = None
    formats: List[str] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)
    doc_number: str = None

    def download(self, path="."):
        from ..api import PublishedImagesApi

        out_file = Path(path) / f"{self.doc_number}.pdf"
        writer = PdfWriter()
        for i in range(1, self.num_pages + 1):
            page_data = PublishedImagesApi.get_page_image_from_link(self.link, page_number=i)
            page = PdfReader(page_data).pages[0]
            if page["/Rotate"] == 90:
                page.rotate_clockwise(-90)
            writer.add_page(page)

        for section in self.sections:
            writer.add_outline_item(section.name.capitalize(), section.start_page)

        with out_file.open("wb") as f:
            writer.write(f)


@dataclass
class Images(InpadocModel):
    __manager__ = "patent_client.epo.ops.published.manager.ImageManager"
    publication_number: str = None
    full_document: ImageDocument = None
    drawing: ImageDocument = None
    first_page: ImageDocument = None

    @property
    def docdb_number(self):
        return str(self.publication_reference)
