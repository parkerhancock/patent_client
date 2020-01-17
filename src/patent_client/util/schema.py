from marshmallow import fields
from .manager import ListManager 

class ListField(fields.List):
    def _deserialize(self, *args, **kwargs):
        out = super(ListField, self)._deserialize(*args, **kwargs)
        return ListManager(out)