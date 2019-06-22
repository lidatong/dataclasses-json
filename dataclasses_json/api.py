import abc
import json
from typing import (Any, Callable, List, Optional, Tuple, Type, TypeVar, Union)

from dataclasses_json.core import (Json, _ExtendedEncoder, _asdict,
                                   _decode_dataclass)
from dataclasses_json.mm import JsonData, SchemaType, build_schema

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
Fields = List[Tuple[str, Any]]


class DataClassJsonMixin(abc.ABC):
    """
    DataClassJsonMixin is an ABC that functions as a Mixin.

    As with other ABCs, it should not be instantiated directly.
    """

    def to_json(self,
                *,
                skipkeys: bool = False,
                ensure_ascii: bool = True,
                check_circular: bool = True,
                allow_nan: bool = True,
                indent: Optional[Union[int, str]] = None,
                separators: Tuple[str, str] = None,
                default: Callable = None,
                sort_keys: bool = False,
                **kw) -> str:
        return json.dumps(_asdict(self),
                          cls=_ExtendedEncoder,
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
    def from_json(cls: Type[A],
                  s: JsonData,
                  *,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None,
                  infer_missing=False,
                  **kw) -> A:
        kvs = json.loads(s,
                         encoding=encoding,
                         parse_float=parse_float,
                         parse_int=parse_int,
                         parse_constant=parse_constant,
                         **kw)
        return cls.from_dict(kvs, infer_missing=infer_missing)

    @classmethod
    def from_dict(cls: Type[A],
                  kvs: Json,
                  *,
                  infer_missing=False) -> A:
        return _decode_dataclass(cls, kvs, infer_missing)

    def to_dict(self):
        return _asdict(self)

    @classmethod
    def schema(cls: Type[A],
               *,
               infer_missing: bool = False,
               only=None,
               exclude=(),
               many: bool = False,
               context=None,
               load_only=(),
               dump_only=(),
               partial: bool = False,
               unknown=None) -> SchemaType:
        Schema = build_schema(cls, DataClassJsonMixin, infer_missing, partial)
        return Schema(only=only,
                      exclude=exclude,
                      many=many,
                      context=context,
                      load_only=load_only,
                      dump_only=dump_only,
                      partial=partial,
                      unknown=unknown)


def dataclass_json(cls):
    cls.to_json = DataClassJsonMixin.to_json
    # unwrap and rewrap classmethod to tag it to cls rather than the literal
    # DataClassJsonMixin ABC
    cls.from_json = classmethod(DataClassJsonMixin.from_json.__func__)
    cls.to_dict = DataClassJsonMixin.to_dict
    cls.from_dict = classmethod(DataClassJsonMixin.from_dict.__func__)
    cls.schema = classmethod(DataClassJsonMixin.schema.__func__)
    # register cls as a virtual subclass of DataClassJsonMixin
    DataClassJsonMixin.register(cls)
    return cls
