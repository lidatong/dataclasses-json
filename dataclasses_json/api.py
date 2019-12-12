import abc
import functools
import json
from dataclasses import fields, Field
from enum import Enum
from typing import (Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar,
                    Union)

from marshmallow.fields import Field as MarshmallowField
from stringcase import camelcase, snakecase, spinalcase, pascalcase  # type: ignore

from dataclasses_json.core import (Json, _ExtendedEncoder, _asdict,
                                   _decode_dataclass, UndefinedParameterAction)
from dataclasses_json.mm import JsonData, SchemaType, build_schema, UndefinedParameterError
from dataclasses_json.utils import _undefined_parameter_action, CatchAll


A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
Fields = List[Tuple[str, Any]]


class LetterCase(Enum):
    CAMEL = camelcase
    KEBAB = spinalcase
    SNAKE = snakecase
    PASCAL = pascalcase


class IgnoreUndefinedParameters(UndefinedParameterAction):
    """
    This action does nothing when it encounters undefined parameters.
    The undefined parameters can not be retrieved after the class has been created.
    """

    @staticmethod
    def handle_from_dict(cls, kvs: Dict) -> Dict[str, Any]:
        known_given_parameters, _ = UndefinedParameterAction._separate_defined_undefined_kvs(cls=cls, kvs=kvs)
        return known_given_parameters


class RaiseUndefinedParameters(UndefinedParameterAction):
    """
    This action raises UndefinedParameterError if it encounters an undefined parameter during initialization.
    """

    @staticmethod
    def handle_from_dict(cls, kvs: Dict) -> Dict[str, Any]:
        known, unknown = UndefinedParameterAction._separate_defined_undefined_kvs(cls=cls, kvs=kvs)
        if len(unknown) > 0:
            raise UndefinedParameterError(f"Received undefined initialization arguments {unknown}")
        return known


class CatchAllUndefinedParameters(UndefinedParameterAction):
    """
    This class allows to add a field of type utils.CatchAll which acts as a dictionary into which all
    undefined parameters will be written.
    These parameters are not affected by LetterCase.
    If no undefined parameters are given, this dictionary will be empty.
    """

    @staticmethod
    def handle_from_dict(cls, kvs: Dict) -> Dict[str, Any]:
        known, unknown = UndefinedParameterAction._separate_defined_undefined_kvs(cls=cls, kvs=kvs)
        catch_all_field = CatchAllUndefinedParameters._get_catch_all_field(cls=cls)
        if catch_all_field.name in known:
            raise UndefinedParameterError(f"Received input parameter with same name as catch-all field: "
                                          f"'{catch_all_field.name}'")
        known[catch_all_field.name] = unknown
        known = {k: v for k, v in known.items() if k not in unknown}
        return known

    @staticmethod
    def handle_to_dict(obj, kvs: Dict[Any, Any]) -> Dict[Any, Any]:
        catch_all_field = CatchAllUndefinedParameters._get_catch_all_field(obj)
        undefined_parameters = kvs.pop(catch_all_field.name)
        kvs.update(undefined_parameters)
        return kvs

    @staticmethod
    def handle_dump(obj) -> Dict[Any, Any]:
        catch_all_field = CatchAllUndefinedParameters._get_catch_all_field(cls=obj)
        return getattr(obj, catch_all_field.name)

    @staticmethod
    def _get_catch_all_field(cls) -> Field:
        catch_all_field = None
        for field in fields(cls):
            if field.type == CatchAll:
                if catch_all_field is not None:
                    raise UndefinedParameterError(
                        f"Multiple catch-all fields supplied: {catch_all_field.name, field.name}.")
                catch_all_field = field
        if catch_all_field is None:
            raise UndefinedParameterError("No field of type dataclasses_json.CatchAll defined")
        return catch_all_field


class UndefinedParameters(Enum):
    """
    Choose the behavior what happens when an undefined parameter is encountered during class initialization.
    """
    INCLUDE = CatchAllUndefinedParameters
    RAISE = RaiseUndefinedParameters
    EXCLUDE = IgnoreUndefinedParameters
    DEFAULT = None  # Same as not specifying a parameter


def config(metadata: dict = None, *,
           encoder: Callable = None,
           decoder: Callable = None,
           mm_field: MarshmallowField = None,
           letter_case: Callable[[str], str] = None,
           undefined_parameters: Optional[Union[str, UndefinedParameters]] = None,
           field_name: str = None) -> Dict[str, dict]:
    if metadata is None:
        metadata = {}

    data = metadata.setdefault('dataclasses_json', {})

    if encoder is not None:
        data['encoder'] = encoder

    if decoder is not None:
        data['decoder'] = decoder

    if mm_field is not None:
        data['mm_field'] = mm_field

    if field_name is not None:
        if letter_case is not None:
            @functools.wraps(letter_case)
            def override(_, _letter_case=letter_case, _field_name=field_name):
                return _letter_case(_field_name)
        else:
            def override(_, _field_name=field_name):
                return _field_name
        letter_case = override

    if letter_case is not None:
        data['letter_case'] = letter_case

    if undefined_parameters is not None:
        # Get the corresponding action for undefined parameters
        if isinstance(undefined_parameters, str):
            try:
                undefined_parameters = UndefinedParameters[undefined_parameters.upper()]
            except KeyError as ke:
                valid_actions = list(action.name for action in UndefinedParameters)
                raise UndefinedParameterError(f"Invalid undefined parameter action, "
                                              f"must be one of {valid_actions}") from ke
        data['undefined_parameters'] = undefined_parameters

    return metadata


class DataClassJsonMixin(abc.ABC):
    """
    DataClassJsonMixin is an ABC that functions as a Mixin.

    As with other ABCs, it should not be instantiated directly.
    """
    dataclass_json_config = None

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
        return json.dumps(self.to_dict(encode_json=False),
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

    def to_dict(self, encode_json=False) -> Dict[str, Json]:
        return _asdict(self, encode_json=encode_json)

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

        if unknown is None:
            undefined_parameter_action = _undefined_parameter_action(cls)
            if undefined_parameter_action is not None:
                # We can just make use of the same-named mm keywords
                unknown = undefined_parameter_action.name.lower()

        return Schema(only=only,
                      exclude=exclude,
                      many=many,
                      context=context,
                      load_only=load_only,
                      dump_only=dump_only,
                      partial=partial,
                      unknown=unknown)


def dataclass_json(_cls=None, *, letter_case=None, undefined_parameters=None):
    """
    Based on the code in the `dataclasses` module to handle optional-parens
    decorators. See example below:

    @dataclass_json
    @dataclass_json(letter_case=Lettercase.CAMEL)
    class Example:
        ...
    """

    def wrap(cls):
        return _process_class(cls, letter_case, undefined_parameters)

    if _cls is None:
        return wrap
    return wrap(_cls)


def _process_class(cls, letter_case, undefined_parameters):
    if letter_case is not None or undefined_parameters is not None:
        cls.dataclass_json_config = config(letter_case=letter_case,
                                           undefined_parameters=undefined_parameters)['dataclasses_json']

    # TODO what to do with __init__?
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
