from yankee.xml import Schema as BaseSchema
from yankee.xml.schema.fields import List as BaseListField

from .schema_mixin import PatentSchemaMixin, ListManagerMixin

class Schema(PatentSchemaMixin, BaseSchema):
    pass

class ListField(ListManagerMixin, BaseListField):
    pass