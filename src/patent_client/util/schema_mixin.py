from importlib import import_module

class PatentSchemaMixin(object):
    __model_name__ = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_name = self.__model_name__ or self.__class__.__name__.replace("Schema", "")
        try:
            model_module = import_module("..model", self.__module__)
            self.__model__ = getattr(model_module, model_name)
        except ModuleNotFoundError:
            model_module = import_module("...model", self.__module__)
            self.__model__ = getattr(model_module, model_name)

    def post_load(self, obj):
        if obj:
            return self.__model__(**obj)
        else:
            return None