from __future__ import annotations

import dataclasses as dc
import datetime as dt
import tempfile
import typing as tp
from pathlib import Path

from patent_client.util import Model
from patent_client.util import one_to_many
from patent_client.util import one_to_one

from .session import session


@dc.dataclass
class ITCInvestigation(Model):
    __manager__ = "patent_client.usitc.manager.ITCInvestigationManager"
    number: str
    phase: str
    status: str
    title: str
    type: str
    docket_number: str = dc.field(default=None)
    documents = one_to_many("patent_client.ITCDocument", investigation_number="number")


@dc.dataclass
class ITCDocument(Model):
    __manager__ = "patent_client.usitc.manager.ITCDocumentManager"
    id: int
    investigation_number: str
    type: str
    title: str
    security: str
    filing_party: str
    filed_by: str
    filed_on_behalf_of: str
    action_jacket_control_number: str
    memorandum_control_number: str
    date: dt.date
    last_modified: dt.date

    investigation = one_to_one("patent_client.ITCInvestigation", investigation_number="investigation_number")
    attachments = one_to_many("patent_client.ITCAttachment", document_id="id")


@dc.dataclass
class ITCAttachment(Model):
    __manager__ = "patent_client.usitc.manager.ITCAttachmentManager"
    id: int
    document_id: int
    title: str
    file_size: int
    file_name: str
    pages: int
    created_date: dt.date
    last_modified_date: dt.date
    document = one_to_one("patent_client.ITCDocument", id="document_id")

    @property
    def download_url(self):
        return f"https://edis.usitc.gov/data/download/{self.document_id}/{self.id}"

    def download(self, file_obj=None):
        *_, ext = self.file_name.split(".")
        if file_obj is None:
            file_obj = tempfile.NamedTemporaryFile(suffix=ext)
        response = session.get(self.download_url, stream=True)
        with file_obj.open("wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return file_obj
