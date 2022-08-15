import importlib
import logging

from .util import resolve

logger = logging.getLogger(__name__)


def get_model(model_name):
    module_name, class_name = model_name.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)


class OneToOne:
    def __init__(self, related_class_name, attribute=None, **mapping):
        self.many = False
        self.related_class_name = related_class_name
        self.attribute = attribute
        self.mapping = mapping

    def __call__(self):
        module_name, class_name = self.related_class_name.rsplit(".", 1)
        related_class = getattr(importlib.import_module(module_name), class_name)
        filter_obj = {k: getattr(self, v) for (k, v) in self.mapping.items()}
        return resolve(related_class.objects.get(**filter_obj), self.attribute)


class OneToMany:
    def __init__(self, related_class_name, **mapping):
        self.many = False
        self.related_class_name = related_class_name
        self.mapping = mapping

    def __call__(self):
        module_name, class_name = self.related_class_name.rsplit(".", 1)
        related_class = getattr(importlib.import_module(module_name), class_name)
        filter_obj = {k: getattr(self, v) for (k, v) in self.mapping.items()}
        return related_class.objects.filter(**filter_obj)


def one_to_one(related_class_name, attribute=None, **mapping):
    many = False  # For use in introspection with inspect.getclosurevars
    module_name, class_name = related_class_name.rsplit(".", 1)

    @property
    def get(self):
        klass = getattr(importlib.import_module(module_name), class_name)
        filter_obj = {k: getattr(self, v) for (k, v) in mapping.items()}
        logger.debug(f"Fetching related {klass} using filter {filter_obj}")
        result = resolve(klass.objects.get(**filter_obj), attribute)
        return result

    return get


def one_to_many(related_class_name, **mapping):
    many = True  # For use in introspection with inspect.getclosurevars
    module_name, class_name = related_class_name.rsplit(".", 1)

    @property
    def get(self):
        klass = getattr(importlib.import_module(module_name), class_name)
        filter_obj = {k: getattr(self, v) for (k, v) in mapping.items()}
        return klass.objects.filter(**filter_obj)

    return get


def get_manager(class_name):
    module_name, class_name = class_name.rsplit(".", 1)

    @property
    def objects(self):
        klass = getattr(importlib.import_module(module_name), class_name)
        return klass()

    return objects


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
