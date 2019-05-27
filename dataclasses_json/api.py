import abc
import json
from typing import Any, Callable, List, Optional, Tuple, TypeVar, Union

from dataclasses_json.mm import build_schema
from dataclasses_json.core import (_ExtendedEncoder, _asdict, _decode_dataclass,
                                   _overrides, _override, JsonTypeInfo, JsonSubtypeInfo)

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
    def from_json(cls: A,
                  s: str,
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
        return _decode_dataclass(cls, kvs, infer_missing)

    @classmethod
    def schema(cls,
               *,
               infer_missing=False,
               only=None,
               exclude=(),
               many=False,
               context=None,
               load_only=(),
               dump_only=(),
               partial=False,
               unknown=None):
        Schema = build_schema(cls, DataClassJsonMixin, infer_missing, partial)
        return Schema(only=only,
                      exclude=exclude,
                      many=many,
                      context=context,
                      load_only=load_only,
                      dump_only=dump_only,
                      partial=partial,
                      unknown=unknown)


def dataclass_json(
        _cls=None, *,
        parse_as_subtype=False,
        subtype_property='@type',
        register_subtype_of=None,
        subtype_id=None):
    """
    Decorator for attaching to_json()/from_json(s) methods to a class.

    Usage Without Parens:
    >>> @dataclass_json
    ... @dataclass
    ... class A:
    ...   x : int
    >>>
    >>> a = A(12)
    >>>
    >>> # Encoing to JSON
    >>> a.to_json()  # '{"x": 12}'
    >>>
    >>> # Decoding from JSON
    >>> a.from_json('{"x": 12}')  # A(x=12)

    Declaring a base class which can delegeate from_json()
    to registered subclasses:
    >>> @dataclass_json(parse_as_subtype=True)
    >>> @dataclass(frozen=True)
    >>> class Base:
    >>>     x: int
    >>> 
    >>> @dataclass_json(register_subtype_of=Base)
    >>> @dataclass(frozen=True)
    >>> class Foo(Base):
    >>>     y: str
    >>> 
    >>> b = Base(1)
    >>> foo = Foo(2, 'abc')
    >>>
    >>> b.to_json()  # '{"x": 1}'
    >>> foo.to_json()  # '{"x": 2, "y": "abc", "@type": "Foo"}'
    >>>
    >>> Base.from_json('{"x": 3}') # Base(3)
    >>> Base.from_json('{"x": 2, "y": "abc", "@type": "Foo"}') # Foo(2, "abc")

    The subtype_property defaults to '@type',
    but can be overriden on the baseclass annotation.

    The subtype_id defaults to the __name__ of the subtype,
    but can be overriden on the subtype annotation.

    Examples:
    >>> @dataclass_json(parse_as_subtype=True, subtype_property='@id')
    >>> @dataclass(frozen=True)
    >>> class Base:
    >>>     x: int
    >>> 
    >>> @dataclass_json(register_subtype_of=Base, subtype_id='f')
    >>> @dataclass(frozen=True)
    >>> class Foo(Base):
    >>>     y: str
    >>> 
    >>> b = Base(1)
    >>> foo = Foo(2, 'abc')
    >>>
    >>> b.to_json()  # '{"x": 1}'
    >>> foo.to_json()  # '{"x": 2, "y": "abc", "@id": "f"}'
    >>>
    >>> Base.from_json('{"x": 3}') # Base(3)
    >>> Base.from_json('{"x": 2, "y": "abc", "@id": "f"}') # Foo(2, "abc")
    """

    def wrap(cls):
        cls.to_json = DataClassJsonMixin.to_json
        # unwrap and rewrap classmethod to tag it to cls rather than the literal
        # DataClassJsonMixin ABC
        cls.from_json = classmethod(DataClassJsonMixin.from_json.__func__)
        cls.schema = classmethod(DataClassJsonMixin.schema.__func__)
        # register cls as a virtual subclass of DataClassJsonMixin
        DataClassJsonMixin.register(cls)

        if parse_as_subtype:
            cls._jsontypeinfo_ = JsonTypeInfo(type_parameter=subtype_property)

        if register_subtype_of is not None:
            basetype = register_subtype_of

            if not hasattr(basetype, '_jsontypeinfo_'):
                raise ValueError(
                    ("@dataclass_json(register_subtype_of=%s) requires "
                     "@dataclass_json(parse_as_subtype=True) on %s")
                        % (basetype.__name__, basetype.__name__))

            key = subtype_id if subtype_id is not None else cls.__name__
            typeinfo = basetype._jsontypeinfo_

            cls._jsonsubtypeinfo_ = JsonSubtypeInfo(typeinfo, key)
            basetype._jsontypeinfo_.add_subtype(key, cls)

        return cls

    if _cls is None:
        return wrap

    return wrap(_cls)

