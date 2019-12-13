from marshmallow import fields
from .manager import QuerySet

class QuerySetField(fields.List):
    def _deserialize(self, *args, **kwargs):
        out = super(QuerySetField, self)._deserialize(*args, **kwargs)
        return QuerySet((out,))