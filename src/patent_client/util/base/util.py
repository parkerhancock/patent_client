import dataclasses
import datetime
from collections import abc


def resolve_list(item, key):
    item_list = resolve(item, key)

    if item_list is None:
        return []

    if isinstance(item_list, list):
        return item_list

    return [item_list]


def resolve_attribute(obj, key):
    if isinstance(obj, abc.Mapping):
        obj = obj[key]
    else:
        obj = getattr(obj, key)
    if callable(obj):
        obj = obj()
    return obj


def resolve(item, key):
    if key is None:
        return item
    accessors = key.split(".")
    try:
        for accessor in accessors:
            if isinstance(item, abc.Sequence) and accessor.isdigit():
                item = item[int(accessor)]
            elif isinstance(item, abc.Sequence) and not accessor.isdigit():
                item = [resolve_attribute(i, accessor) for i in item]
            else:
                item = resolve_attribute(item, accessor)
    except Exception as e:
        return None
    return item


def to_dict(obj, item_class=dict, collection_class=list):
    # print(f"Obj is {obj}")
    if isinstance(obj, abc.Mapping):
        # print(f"Casting as Mapping with class {item_class}")
        return item_class((k, to_dict(v, item_class, collection_class, convert_dates)) for k, v in obj.items())
    elif dataclasses.is_dataclass(obj):
        # print("Converting Dataclass")
        return to_dict(item_class(obj), item_class, collection_class, convert_dates)
    elif isinstance(obj, abc.Iterable) and not isinstance(obj, (str, bytes)):
        # print(f"Casting as Collection with {collection_class}")
        return collection_class(to_dict(i, item_class, collection_class, convert_dates) for i in obj)
    elif convert_dates and isinstance(obj, datetime.date):
        return datetime.datetime.combine(obj, datetime.datetime.min.time())
    else:
        # print("No cast - passing through")
        return obj
