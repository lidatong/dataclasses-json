import json
from typing import List, Optional, Set, Tuple

from dataclasses import asdict, fields, is_dataclass


class _Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Set):
            return list(o)
        return json.JSONEncoder.default(self, o)


class DataClassJsonMixin:
    def to_json(self, skipkeys=False, ensure_ascii=True, check_circular=True,
                allow_nan=True, indent=None, separators=None,
                default=None, sort_keys=False, **kw):
        return json.dumps(asdict(self),
                          cls=_Encoder,
                          skipkeys=skipkeys,
                          ensure_ascii=ensure_ascii,
                          check_circular=check_circular,
                          allow_nan=allow_nan,
                          indent=indent,
                          separators=separators,
                          default=default,
                          sort_keys=sort_keys,
                          **kw)

    @classmethod
    def from_json(cls,
                  kvs,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None):
        init_kwargs = json.loads(kvs,
                                 encoding=encoding,
                                 parse_float=parse_float,
                                 parse_int=parse_int,
                                 parse_constant=parse_constant)
        return _from_dict(cls, init_kwargs)


_supported_collections = {List, Set, Tuple}


def _from_dict(cls, kvs):
    init_kwargs = {}
    for field in fields(cls):
        if is_dataclass(field.type):
            init_kwargs[field.name] = _from_dict(field.type, kvs[field.name])
        elif any(_issubclass_safe(field.type, c_type)
                 for c_type in _supported_collections):
            type_arg = field.type.__args__[0]
            if is_dataclass(type_arg):
                xs = (_from_dict(type_arg, v) for v in kvs[field.name])
            else:
                xs = kvs[field.name]
            if _issubclass_safe(field.type, Tuple):
                init_kwargs[field.name] = tuple(xs)
            elif _issubclass_safe(field.type, Set):
                init_kwargs[field.name] = set(xs)
            else:
                init_kwargs[field.name] = list(xs)
        elif (_issubclass_safe(field.type, Optional)
              or _hasargs(field.type, type(None))):
            type_arg = field.type.__args__[0]
            value = kvs[field.name]
            if is_dataclass(type_arg) and value is not None:
                init_kwargs[field.name] = _from_dict(type_arg, value)
            else:
                init_kwargs[field.name] = value
        else:
            init_kwargs[field.name] = kvs[field.name]
    return cls(**init_kwargs)


def _issubclass_safe(cls, classinfo):
    try:
        result = issubclass(cls, classinfo)
    except TypeError:
        return False
    else:
        return result


def _hasargs(type_, *args):
    try:
        res = all(arg in type_.__args__ for arg in args)
    except AttributeError:
        return False
    else:
        return res
