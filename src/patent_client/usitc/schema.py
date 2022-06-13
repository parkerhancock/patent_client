import importlib
import xml.etree.ElementTree as ET

from marshmallow import EXCLUDE
from marshmallow import Schema
from marshmallow import fields
from marshmallow import post_load
from marshmallow import pre_load

from patent_client.util.manager import resolve

# from .model import ITCInvestigation, ITCDocument, ITCAttachment


class BaseSchema(Schema):
    def __init__(self, *args, **kwargs):
        super(BaseSchema, self).__init__(*args, **kwargs)
        parent_module = __name__.rsplit(".", 1)[0]
        models = importlib.import_module(".model", parent_module)
        self.__model__ = getattr(models, self.__class__.__name__.replace("Schema", ""))

    @post_load
    def make_object(self, data, **kwargs):
        if hasattr(self, "__model__"):
            return self.__model__(**data)
        return data


class ITCInvestigationSchema(BaseSchema):
    number = fields.Str()
    phase = fields.Str()
    status = fields.Str()
    title = fields.Str()
    type = fields.Str()
    docket_number = fields.Str(allow_none=True)

    @pre_load
    def pre_load(self, xml_string, *args, **kwargs):
        tree = ET.fromstring(xml_string)[0][0]
        return {
            "phase": tree.find("investigationPhase").text,
            "number": tree.find("investigationNumber").text,
            "status": tree.find("investigationStatus").text,
            "title": tree.find("investigationTitle").text,
            "type": tree.find("investigationType").text,
            "docket_number": tree.find("docketNumber").text,
        }


class ITCDocumentSchema(BaseSchema):
    id = fields.Int()
    investigation_number = fields.Str()
    type = fields.Str()
    title = fields.Str(allow_none=True)
    security = fields.Str()
    filing_party = fields.Str()
    filed_by = fields.Str()
    filed_on_behalf_of = fields.Str(allow_none=True)
    action_jacket_control_number = fields.Str(allow_none=True)
    memorandum_control_number = fields.Str(allow_none=True)
    date = fields.Date()
    last_modified = fields.DateTime()

    @pre_load
    def pre_load(self, etree_el, *args, **kwargs):
        attribute_dict = dict(
            type="documentType",
            title="documentTitle",
            security="securityLevel",
            investigation_number="investigationNumber",
            filing_party="firmOrganization",
            filed_by="filedBy",
            filed_on_behalf_of="onBehalfOf",
            action_jacket_control_number="actionJacketControlNumber",
            memorandum_control_number="memorandumControlNumber",
            date="documentDate",
            last_modified="modifiedDate",
            id="id",
        )
        data = dict()
        for key, value in attribute_dict.items():
            data[key] = etree_el.find(value).text
        return data

    class Meta:
        dateformat = "%Y/%m/%d 00:00:00"
        datetimeformat = "%Y/%m/%d %H:%M:%S"


class ITCAttachmentSchema(BaseSchema):
    id = fields.Int()
    document_id = fields.Int()
    title = fields.Str()
    file_size = fields.Int()
    file_name = fields.Str()
    pages = fields.Int()
    created_date = fields.DateTime(format="%Y/%m/%d %H:%M:%S")
    last_modified_date = fields.DateTime(format="%Y/%m/%d %H:%M:%S")

    @pre_load
    def pre_load(self, etree_el, *args, **kwargs):
        attribute_dict = dict(
            id="id",
            document_id="documentId",
            title="title",
            file_size="fileSize",
            file_name="originalFileName",
            pages="pageCount",
            created_date="createDate",
            last_modified_date="lastModifiedDate",
        )
        data = dict()
        for k, value in attribute_dict.items():
            data[k] = etree_el.find(value).text
        return data
