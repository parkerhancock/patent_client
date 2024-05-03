import random

random.seed(1)


def compare_lists(list_1, list_2, key=""):
    for i, item in enumerate(list_1):
        if isinstance(item, list) and not isinstance(item, str):
            return compare_lists(item, list_2[i], key=f"{key}.{i}")
        elif isinstance(item, dict):
            return compare_dicts(item, list_2[i], key=f"{key}.{i}")
        else:
            assert item == list_2[i], f"At key {key}.{i}, {item} != {list_2[i]}"


def compare_dicts(dict_1, dict_2, key=""):
    dict_1_keys = set(dict_1.keys())
    dict_2_keys = set(dict_2.keys())
    in_1_not_2 = dict_1_keys - dict_2_keys
    in_2_not_1 = dict_2_keys - dict_1_keys
    if len(in_1_not_2) > 0:
        raise ValueError(f"At {key}, Keys {in_1_not_2} are in Dict 1, but not Dict 2")
    if len(in_2_not_1) > 0:
        raise ValueError(f"At {key}, Keys {in_2_not_1} are not in Dict 1, but are in Dict 2")

    for k, v in dict_1.items():
        if isinstance(v, list) and not isinstance(v, str):
            return compare_lists(v, dict_2[k], key=f"{key}.{k}")
        elif isinstance(v, dict):
            return compare_dicts(v, dict_2[k], key=f"{key}.{k}")
        else:
            assert v == dict_2[k], f"At key {key}.{k}, {v} != {dict_2[k]}"
