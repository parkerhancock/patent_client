
from yankee.json import Schema as Schema

from .schema_mixin import PatentSchemaMixin
from .model import Model

class Schema(PatentSchemaMixin, Schema):
    pass

