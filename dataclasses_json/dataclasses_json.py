import json
from typing import List, Optional, Set, Tuple, Union, FrozenSet, Deque, Collection
from collections import deque

from dataclasses import asdict, fields, is_dataclass

_cons_map = {List: list,
             Set: set,
             Tuple: tuple,
             FrozenSet: frozenset,
             Deque: deque}


class _Encoder(json.JSONEncoder):
    def default(self, o):
        if any(isinstance(o, c_type) for c_type in _cons_map):
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
        return _decode_dataclass(cls, init_kwargs)


def _decode_dataclass(cls, kvs):
    init_kwargs = {}
    for field in fields(cls):
        field_value = kvs[field.name]
        if is_dataclass(field_value):
            init_kwargs[field.name] = _decode_dataclass(field.type, field_value)
        elif _is_supported_generic(field.type):
            init_kwargs[field.name] = _decode_generic(field.type, field_value)
        else:
            init_kwargs[field.name] = field_value
    return cls(**init_kwargs)


def _is_supported_generic(type_):
    is_collection = any(_issubclass_safe(type_, generic_type)
                        for generic_type in _cons_map)
    is_optional = (_issubclass_safe(type_, Optional)
                   or _hasargs(type_, type(None)))
    return is_collection or is_optional


def _get_cons(type_, *, default):
    for c_type, cons in _cons_map.items():
        if _issubclass_safe(type_, c_type):
            return cons
    return default


def _decode_generic(type_, value):
    if not value:
        res = value
    elif any(_issubclass_safe(type_, c_type) for c_type in _cons_map):
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
        res = _get_cons(type_, default=type(value))(xs)
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


from typing import Generic, TypeVar
from dataclasses import dataclass

A = TypeVar('A')


@dataclass(frozen=True)
class Nested(Generic[A], DataClassJsonMixin):
    value: Optional[FrozenSet[A]]


nested_json = Nested(frozenset([5])).to_json()
print(Nested.from_json(nested_json))

