import re

from yankee.xml import fields as f

from patent_client.epo.ops.number_service.schema import DocumentIdSchema
from patent_client.epo.ops.util import Schema
from patent_client.util.xml import ListField

doc_number_re = re.compile(r"published-data/images/(?P<country>[^/]+)/(?P<doc_number>[^/]+)/(?P<kind_code>[^/]+)/")


def get_doc_number(string):
    data = doc_number_re.search(string).groupdict()
    return f"{data['country']}{data['doc_number']}{data['kind_code']}"


class SectionSchema(Schema):
    name = f.Str("./@name")
    start_page = f.Int("./@start-page")


class ImageDocumentSchema(Schema):
    num_pages = f.Int("./@number-of-pages")
    description = f.Str("./@desc")
    link = f.Str("./@link")
    formats = ListField(f.Str(), "./ops:document-format-options/ops:document-format")
    sections = ListField(SectionSchema, "./ops:document-section")
    doc_number = f.Str("./@link", formatter=get_doc_number)


class ImagesSchema(Schema):
    search_reference = DocumentIdSchema(".//ops:document-inquiry/ops:publication-reference")
    publication_reference = DocumentIdSchema(".//ops:inquiry-result/epo:publication-reference")
    documents = ListField(ImageDocumentSchema, ".//ops:document-instance")
