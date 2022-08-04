from collections import abc
import dataclasses

def resolve(item, key):
    if key is None:
        return item
    accessors = key.split(".")
    try:
        for accessor in accessors:
            if accessor.isdigit():
                item = item[int(accessor)]
            elif isinstance(item, dict):
                item = item[accessor]
            else:
                item = getattr(item, accessor)
            if callable(item):
                item = item()
    except Exception as e:
        return None
    return item


def resolve_list(item, key):
    item_list = resolve(item, key)

    if item_list is None:
        return []

    if isinstance(item_list, list):
        return item_list

    return [item_list]

def to_dict(obj, item_class=dict, collection_class=list):
    #print(f"Obj is {obj}")
    if isinstance(obj, abc.Mapping):
        #print(f"Casting as Mapping with class {item_class}")
        return item_class((k, to_dict(v, item_class, collection_class)) for k, v in obj.items())
    elif dataclasses.is_dataclass(obj):
        #print("Converting Dataclass")
        return to_dict(item_class(obj), item_class, collection_class)
    elif isinstance(obj, abc.Iterable) and not isinstance(obj, (str, bytes)):
        #print(f"Casting as Collection with {collection_class}")
        return collection_class(to_dict(i, item_class, collection_class) for i in obj)
    else:
        #print("No cast - passing through")
        return obj
