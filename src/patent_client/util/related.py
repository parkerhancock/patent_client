import importlib

from .manager import QuerySet


def one_to_one(class_name, **mapping):
    module_name, class_name = class_name.rsplit(".", 1)

    @property
    def get(self):
        try:
            klass = getattr(importlib.import_module(module_name), class_name)
            filter_obj = {k: getattr(self, v) for (k, v) in mapping.items()}
            return klass.objects.get(**filter_obj)
        except AttributeError:
            return None

    return get


def one_to_many(class_name, **mapping):
    module_name, class_name = class_name.rsplit(".", 1)

    @property
    def get(self):
        klass = getattr(importlib.import_module(module_name), class_name)
        filter_obj = {k: getattr(self, v) for (k, v) in mapping.items()}
        return klass.objects.filter(**filter_obj)

    return get


def recur_accessor(obj, accessor):
    if "__" not in accessor:
        a = accessor
        rest = None
    else:
        a, rest = accessor.split("__", 1)

    if hasattr(obj, a):
        new_obj = getattr(obj, a)
        if callable(new_obj):
            new_obj = new_obj()
    else:
        try:
            a = int(a)
        except ValueError:
            pass
        try:
            new_obj = obj[a]
        except (KeyError, TypeError, IndexError):
            new_obj = None
    if not rest:
        return new_obj
    else:
        return recur_accessor(new_obj, rest)
