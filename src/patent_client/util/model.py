from collections import OrderedDict
from dataclasses import dataclass, fields

from .manager import QuerySet

@dataclass
class Model():
    def as_dict(self):
        output = OrderedDict()
        for k, v in self:
            if isinstance(v, Model):
                output[k] = v.as_dict()
            elif isinstance(v, (list, QuerySet)):
                output[k] = [i.as_dict() if hasattr(i, 'as_dict') else i for i in v]
            else:
                output[k] = v
        return output

    def fields(self):
        return fields(self)

    def __iter__(self):
        for f in sorted(self.fields(), key=lambda x: x.name):
            if hasattr(self, f.name):
                yield (f.name, getattr(self, f.name))
    
    def to_pandas(self):
        import pandas as pd
        return pd.Series(self.as_dict())
