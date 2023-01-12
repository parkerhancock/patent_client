import re

from patent_client.epo.ops.util import Schema
from yankee.xml import fields as f

doc_number_re = re.compile(r"published-data/images/(?P<country>[^/]+)/(?P<doc_number>[^/]+)/(?P<kind_code>[^/]+)/")


def get_doc_number(string):
    data = doc_number_re.search(string).groupdict()
    return f"{data['country']}{data['doc_number']}{data['kind_code']}"


class DocDbSchema(f.Combine):
    country = f.Str('.//epo:document-id[@document-id-type="docdb"]/epo:country')
    doc_number = f.Str('.//epo:document-id[@document-id-type="docdb"]/epo:doc-number')
    kind = f.Str('.//epo:document-id[@document-id-type="docdb"]/epo:kind')

    def combine_func(self, obj):
        return f"{obj.country}{obj.doc_number}{obj.kind}"


class SectionSchema(Schema):
    name = f.Str("./@name")
    start_page = f.Int("./@start-page")


class ImageDocumentSchema(Schema):
    num_pages = f.Int("./@number-of-pages")
    description = f.Str("./@desc")
    link = f.Str("./@link")
    formats = f.List(f.Str(), "./ops:document-format-options/ops:document-format")
    sections = f.List(SectionSchema, "./ops:document-section")
    doc_number = f.Str("./@link", formatter=get_doc_number)


class ImagesSchema(Schema):
    # search_reference = DocumentIdSchema(".//ops:document-inquiry/ops:publication-reference")
    publication_number = DocDbSchema(".//ops:inquiry-result/epo:publication-reference")
    full_document = ImageDocumentSchema('.//ops:document-instance[@desc="FullDocument"]')
    drawing = ImageDocumentSchema('.//ops:document-instance[@desc="Drawing"]')
    first_page = ImageDocumentSchema('.//ops:document-instance[@desc="FirstPageClipping"]')
