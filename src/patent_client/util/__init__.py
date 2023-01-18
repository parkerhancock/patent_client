from .base.manager import Manager
from .base.manager import ModelType
from .base.model import Model
from .base.related import get_manager
from .base.related import one_to_many
from .base.related import one_to_one


class DefaultDict(dict):
    def __init__(self, *args, default=None, **kwargs):
        self.default = default
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        return self.default


__all__ = [
    "DefaultDict",
    "Manager",
    "ModelType",
    "Model",
    "get_manager",
    "one_to_many",
    "one_to_one",
]
