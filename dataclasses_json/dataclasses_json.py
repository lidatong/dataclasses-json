import json
from dataclasses import asdict, fields, is_dataclass
from typing import Collection, Optional
from collections import ChainMap


class _Encoder(json.JSONEncoder):
    def default(self, o):
        if _isinstance_safe(o, Collection):
            return list(o)
        return json.JSONEncoder.default(self, o)


class DataClassJsonMixin:
    def to_json(self, *, skipkeys=False, ensure_ascii=True, check_circular=True,
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
                  *,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None,
                  infer_missing=False):
        init_kwargs = json.loads(kvs,
                                 encoding=encoding,
                                 parse_float=parse_float,
                                 parse_int=parse_int,
                                 parse_constant=parse_constant)

        if infer_missing:
            init_kwargs = ChainMap(init_kwargs,
                                   {field.name: None for field in fields(cls)
                                    if field.name not in init_kwargs})
        return _decode_dataclass(cls, init_kwargs)

    @classmethod
    def from_json_array(cls,
                        kvss,
                        encoding=None,
                        parse_float=None,
                        parse_int=None,
                        parse_constant=None):
        init_kwargs_array = json.loads(kvss,
                                       encoding=encoding,
                                       parse_float=parse_float,
                                       parse_int=parse_int,
                                       parse_constant=parse_constant)
        return [_decode_dataclass(cls, init_kwargs)
                for init_kwargs in init_kwargs_array]


def _decode_dataclass(cls, kvs):
    init_kwargs = {}
    for field in fields(cls):
        field_value = kvs[field.name]
        if is_dataclass(field.type):
            init_kwargs[field.name] = _decode_dataclass(field.type, field_value)
        elif _is_supported_generic(field.type) and field.type != str:
            init_kwargs[field.name] = _decode_generic(field.type, field_value)
        else:
            init_kwargs[field.name] = field_value
    return cls(**init_kwargs)


def _is_supported_generic(type_):
    try:
        is_collection = _issubclass_safe(type_.__origin__, Collection)
    except AttributeError:
        return False
    is_optional = (_issubclass_safe(type_, Optional)
                   or _hasargs(type_, type(None)))
    return is_collection or is_optional


def _decode_generic(type_, value):
    if value is None:
        res = value
    elif _issubclass_safe(type_.__origin__, Collection):
        # this is a tricky situation where we need to check both the annotated
        # type info (which is usually a type from `typing`) and check the
        # value's type directly using `type()`.
        #
        # if the type_arg is a generic we can use the annotated type, but if the
        # type_arg is a typevar we need to extract the reified type information
        # hence the check of `is_dataclass(value)`
        type_arg = type_.__args__[0]
        if is_dataclass(type_arg) or is_dataclass(value):
            xs = (_decode_dataclass(type_arg, v) for v in value)
        elif _is_supported_generic(type_arg):
            xs = (_decode_generic(type_arg, v) for v in value)
        else:
            xs = value
        # get the constructor if using corresponding generic type in `typing`
        # otherwise fallback on the type returned by
        try:
            res = type_.__origin__(xs)
        except TypeError:
            res = type_(xs)
    else:  # Optional
        type_arg = type_.__args__[0]
        if is_dataclass(type_arg) or is_dataclass(value):
            res = _decode_dataclass(type_arg, value)
        elif _is_supported_generic(type_arg):
            res = _decode_generic(type_arg, value)
        else:
            res = value
    return res


def _issubclass_safe(cls, classinfo):
    try:
        result = issubclass(cls, classinfo)
    except Exception:
        return False
    else:
        return result


def _isinstance_safe(o, t):
    try:
        result = isinstance(o, t)
    except Exception:
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
