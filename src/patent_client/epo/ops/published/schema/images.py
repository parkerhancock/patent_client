import re

from yankee.xml import fields as f
from patent_client.epo.ops.util import Schema
from patent_client.epo.ops.number_service.schema import DocumentIdSchema

class SectionSchema(Schema):
    name = f.Str("./@name")
    start_page = f.Str("./@start-page")

class ImageDocumentSchema(Schema):
    num_pages = f.Int("./@number-of-pages")
    description = f.Str("./@desc")
    link = f.Str("./@link")
    formats = f.List(f.Str(), "./ops:document-format-options/ops:document-format")
    sections = f.List(SectionSchema, "./ops:document-section")

class ImagesSchema(Schema):
    search_reference = DocumentIdSchema(".//ops:document-inquiry/ops:publication-reference")
    publication_reference = DocumentIdSchema(".//ops:inquiry-result/epo:publication-reference")
    documents = f.List(ImageDocumentSchema, ".//ops:document-instance")

