import importlib


def get_model(model_name):
    module_name, class_name = model_name.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), class_name)
