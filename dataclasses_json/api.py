import abc
import json
from dataclasses import fields
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union

from marshmallow import Schema, post_load

from dataclasses_json import mm
from dataclasses_json.core import (_CollectionEncoder, _asdict,
                                   _decode_dataclass)

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
                          cls=_CollectionEncoder,
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
    def from_json(cls: A,
                  s: str,
                  *,
                  encoding=None,
                  parse_float=None,
                  parse_int=None,
                  parse_constant=None,
                  infer_missing=False,
                  **kw) -> A:
        init_kwargs = json.loads(s,
                                 encoding=encoding,
                                 parse_float=parse_float,
                                 parse_int=parse_int,
                                 parse_constant=parse_constant,
                                 **kw)
        return _decode_dataclass(cls, init_kwargs, infer_missing)

    @classmethod
    def schema(cls,
               *,
               only=None,
               exclude=(),
               many=False,
               context=None,
               load_only=(),
               dump_only=(),
               partial=False,
               unknown=None):
        Meta = type('Meta',
                    (),
                    {'fields': tuple(field.name for field in fields(cls))})

        @post_load
        def make_instance(self, kvs):
            return _decode_dataclass(cls, kvs, infer_missing=partial)

        fields_ = fields(cls)
        nested_fields = mm._make_nested_fields(fields_, DataClassJsonMixin)
        primitive_fields = [field for field in fields_
                            if field.name not in nested_fields]
        default_fields = mm._make_default_fields(primitive_fields, cls)
        DataClassSchema = type(f'{cls.__name__.capitalize()}Schema',
                               (Schema,),
                               {'Meta': Meta,
                                f'make_{cls.__name__.lower()}': make_instance,
                                **nested_fields,
                                **default_fields})
        return DataClassSchema(only=only,
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
    cls.schema = classmethod(DataClassJsonMixin.schema.__func__)
    # register cls as a virtual subclass of DataClassJsonMixin
    DataClassJsonMixin.register(cls)
    return cls
