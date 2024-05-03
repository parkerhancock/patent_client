import datetime
import typing as tp
from pathlib import Path

from pydantic import Field

from patent_client.util.pydantic_util import BaseModel


class File(BaseModel):
    link_path: str = Field(alias="fileLinkPath")
    identifier: int = Field(alias="fileIdentifier")
    name: str = Field(alias="fileName")
    size: int = Field(alias="fileSize")
    download_url: str = Field(alias="fileDownloadUrl")
    from_date: datetime.date = Field(alias="fileFromTime")
    to_date: datetime.date = Field(alias="fileToTime")
    type: str = Field(alias="fileType")
    release_date: datetime.date = Field(alias="fileReleaseDate")

    async def download(self, path: tp.Optional[tp.Union[str, Path]]):
        from .api import client

        return await client.download(self.download_url, path=path)


class Product(BaseModel):
    link_path: str = Field(alias="productLinkPath")
    identifier: int = Field(alias="productIdentifier")
    short_name: str = Field(alias="productShortName")
    description: str = Field(alias="productDesc")
    title: str = Field(alias="productTitle")
    frequency: tp.Optional[str] = Field(alias="productFrequency", default=None)
    level: str = Field(alias="productLevel")
    from_date: datetime.date = Field(alias="productFromDate")
    to_date: datetime.date = Field(alias="productToDate")
    number_of_files: int = Field(alias="numberOfFiles")
    parent_product: tp.Optional[str] = Field(alias="parentProduct", default=None)
    files: tp.Optional[tp.List[File]] = Field(alias="productFiles", default_factory=list)
