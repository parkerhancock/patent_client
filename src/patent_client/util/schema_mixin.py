from importlib import import_module
from .manager import ListManager

class PatentSchemaMixin(object):
    __model_name__ = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            model_name = self.__model_name__ or self.__class__.__name__.replace("Schema", "")
            try:
                model_module = import_module("..model", self.__module__)
                self.__model__ = getattr(model_module, model_name)
            except (ModuleNotFoundError, AttributeError):
                model_module = import_module("...model", self.__module__)
                self.__model__ = getattr(model_module, model_name)
        except (ModuleNotFoundError, ImportError, AttributeError):
            self.__model__ = None

    def post_load(self, obj):
        try:
            if obj and self.__model__:
                return self.__model__(**obj)
            elif obj:
                return obj
            else:
                return None
        except AttributeError:
            breakpoint()

class ListManagerMixin(object):
    def deserialize(self, obj):
        obj = super().deserialize(obj)
        return ListManager(obj)
