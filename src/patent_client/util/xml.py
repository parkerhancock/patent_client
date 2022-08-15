from yankee.xml import Schema as BaseSchema, RegexSchema as BaseRegexSchema, fields as f, fields
from yankee.xml.schema.fields import List as BaseListField
from yankee.util import clean_whitespace, unzip_records

from .schema_mixin import ListManagerMixin
from .schema_mixin import PatentSchemaMixin


class Schema(PatentSchemaMixin, BaseSchema):
    pass

class ListField(ListManagerMixin, BaseListField):
    pass

class RegexSchema(PatentSchemaMixin, BaseRegexSchema):
    pass

class TailField(f.Field):
    """Field to retreive tail text"""
    def load(self, obj):
        return super().load(obj)

    def deserialize(self, obj):
        return clean_whitespace(super().deserialize(obj).tail)

class ZipSchema(Schema):
    """
    This schema type allows fields that produce multiple values to be
    zipped together into records.
    """
    def bind(self, name=None, parent=None):
        super().bind(name, parent)
        new_fields = dict()
        for name, field in self.fields.items():
            new_fields[name] = f.List(field.__class__, getattr(field.accessor, "data_key", None))
        self.fields = new_fields

    def deserialize(self, obj) -> "Dict":
        result = super().deserialize(obj)
        result = unzip_records(result)
        return result