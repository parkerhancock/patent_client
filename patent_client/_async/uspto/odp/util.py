import typing as tp


def prune(obj: tp.Any) -> tp.Any:
    if isinstance(obj, dict):
        return {
            k: prune(v)
            for k, v in obj.items()
            if v is not None and not (isinstance(v, tp.Collection) and len(v) == 0)
        }
    elif isinstance(obj, list):
        return [
            prune(v)
            for v in obj
            if v is not None and not (isinstance(v, tp.Collection) and len(v) == 0)
        ]
    else:
        return obj
