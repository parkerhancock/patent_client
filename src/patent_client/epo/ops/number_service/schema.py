from patent_client.epo.ops.util import Schema
from yankee.xml import fields as f

from . import error_dir


class TagField(f.Field):
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        if obj is None:
            return None
        return obj.tag.split("}")[1].split("-")[0]


class DocumentIdSchema(Schema):
    doc_type = TagField("./*")
    id_type = f.Str(".//@document-id-type")
    country = f.Str(".//epo:country")
    number = f.Str(".//epo:doc-number")
    kind = f.Str(".//epo:kind")
    date = f.Date(".//epo:date")
    name = f.Str(".//epo:name")


def get_messages(text):
    return [error_dir[k] for k in text.split() if k != "SUCCESS"]


class NumberServiceResultSchema(Schema):
    input_doc = DocumentIdSchema(".//ops:input")
    output_doc = DocumentIdSchema(".//ops:output")
    service_version = f.Str('.//ops:meta[@name="version"]/@value')
    messages = f.Str('.//ops:meta[@name="status"]/@value', formatter=get_messages)
