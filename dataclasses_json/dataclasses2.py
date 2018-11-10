import copy
from dataclasses import _is_dataclass_instance, fields
from typing import Collection, Mapping


def asdict2(obj):
    """
    A re-implementation of `asdict` (based on the original in the `dataclasses`
    source) to support arbitrary Collection and Mapping types.
    """
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = asdict2(getattr(obj, f.name))
            result.append((f.name, value))
        return dict(result)
    elif isinstance(obj, Mapping):
        return dict(
            (asdict2(k), asdict2(v))
            for k, v in obj.items())
    elif isinstance(obj, Collection) and not isinstance(obj, str):
        return list(asdict2(v) for v in obj)
    else:
        return copy.deepcopy(obj)
