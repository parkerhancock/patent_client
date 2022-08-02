from yankee.json import Schema as Schema

from .model import Model
from .schema_mixin import PatentSchemaMixin


class Schema(PatentSchemaMixin, Schema):
    pass
