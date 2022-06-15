from yankee.json import Schema as Schema

from .schema_mixin import PatentSchemaMixin

class Schema(PatentSchemaMixin, Schema):
    pass
