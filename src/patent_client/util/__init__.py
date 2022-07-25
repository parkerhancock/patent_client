from .manager import ListManager
from .manager import Manager
from .manager import ModelType
from .manager import QuerySet
from .model import Model
from .related import get_manager
from .related import one_to_many
from .related import one_to_one

class DefaultDict(dict):
    def __init__(self, *args, default=None, **kwargs):
        self.default = default
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        return self.default

