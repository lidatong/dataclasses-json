import typing
import warnings
import sys
from copy import deepcopy

from dataclasses import MISSING, is_dataclass, fields as dc_fields
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum

from typing_inspect import is_union_type  # type: ignore

from marshmallow import fields, Schema, post_load, types
from marshmallow_enum import EnumField  # type: ignore
from marshmallow.exceptions import ValidationError

from dataclasses_json.core import (_is_supported_generic, _decode_dataclass,
                                   _ExtendedEncoder, _user_overrides)
from dataclasses_json.utils import (_is_collection, _is_optional,
                                    _issubclass_safe, _timestamp_to_dt_aware,
                                    _is_new_type, _get_type_origin,
                                    _handle_undefined_parameters_save, CatchAll)


class _TimestampField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is not None:
            return value.timestamp()
        else:
            if not self.required:
                return None
            else:
                raise ValidationError(self.default_error_messages["required"])

    def _deserialize(self, value, attr, data, **kwargs):
        if value is not None:
            return _timestamp_to_dt_aware(value)
        else:
            if not self.required:
                return None
            else:
                raise ValidationError(self.default_error_messages["required"])


class _IsoField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is not None:
            return value.isoformat()
        else:
            if not self.required:
                return None
            else:
                raise ValidationError(self.default_error_messages["required"])

    def _deserialize(self, value, attr, data, **kwargs):
        if value is not None:
            return datetime.fromisoformat(value)
        else:
            if not self.required:
                return None
            else:
                raise ValidationError(self.default_error_messages["required"])


class _UnionField(fields.Field):
    def __init__(self, desc, cls, field, *args, **kwargs):
        self.desc = desc
        self.cls = cls
        self.field = field
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if self.allow_none and value is None:
            return None
        for type_, schema_ in self.desc.items():
            if _issubclass_safe(type(value), type_):
                if is_dataclass(value):
                    res = schema_._serialize(value, attr, obj, **kwargs)
                    res['__type'] = str(type_.__name__)
                    return res
                break
            elif isinstance(value, _get_type_origin(type_)):
                return schema_._serialize(value, attr, obj, **kwargs)
        else:
            warnings.warn(
                f'The type "{type(value).__name__}" (value: "{value}") '
                f'is not in the list of possible types of typing.Union '
                f'(dataclass: {self.cls.__name__}, field: {self.field.name}). '
                f'Value cannot be serialized properly.')
        return super()._serialize(value, attr, obj, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        tmp_value = deepcopy(value)
        if isinstance(tmp_value, dict) and '__type' in tmp_value:
            dc_name = tmp_value['__type']
            for type_, schema_ in self.desc.items():
                if is_dataclass(type_) and type_.__name__ == dc_name:
                    del tmp_value['__type']
                    return schema_._deserialize(tmp_value, attr, data, **kwargs)
        for type_, schema_ in self.desc.items():
            if isinstance(tmp_value, _get_type_origin(type_)):
                return schema_._deserialize(tmp_value, attr, data, **kwargs)
        else:
            warnings.warn(
                f'The type "{type(tmp_value).__name__}" (value: "{tmp_value}") '
                f'is not in the list of possible types of typing.Union '
                f'(dataclass: {self.cls.__name__}, field: {self.field.name}). '
                f'Value cannot be deserialized properly.')
        return super()._deserialize(tmp_value, attr, data, **kwargs)


TYPES = {
    typing.Mapping: fields.Mapping,
    typing.MutableMapping: fields.Mapping,
    typing.List: fields.List,
    typing.Dict: fields.Dict,
    typing.Tuple: fields.Tuple,
    typing.Callable: fields.Function,
    dict: fields.Dict,
    list: fields.List,
    str: fields.Str,
    int: fields.Int,
    float: fields.Float,
    bool: fields.Bool,
    datetime: _TimestampField,
    UUID: fields.UUID,
    Decimal: fields.Decimal,
    CatchAll: fields.Dict,
}

A = typing.TypeVar('A')
JsonData = typing.Union[str, bytes, bytearray]
TEncoded = typing.Dict[str, typing.Any]
TOneOrMulti = typing.Union[typing.List[A], A]
TOneOrMultiEncoded = typing.Union[typing.List[TEncoded], TEncoded]

if sys.version_info >= (3, 7):
    class SchemaF(Schema, typing.Generic[A]):
        """Lift Schema into a type constructor"""

        def __init__(self, *args, **kwargs):
            """
            Raises exception because this class should not be inherited.
            This class is helper only.
            """

            super().__init__(*args, **kwargs)
            raise NotImplementedError()

        @typing.overload
        def dump(self, obj: typing.List[A], many: bool = None) -> typing.List[TEncoded]:  # type: ignore
            pass  # mm has the wrong return type annotation (dict) so we can ignore the mypy error

        @typing.overload
        def dump(self, obj: A, many: bool = None) -> TEncoded:
            pass

        def dump(self, obj: TOneOrMulti,
                 many: bool = None) -> TOneOrMultiEncoded:
            pass

        @typing.overload
        def dumps(self, obj: typing.List[A], many: bool = None, *args,
                  **kwargs) -> str:
            pass

        @typing.overload
        def dumps(self, obj: A, many: bool = None, *args, **kwargs) -> str:
            pass

        def dumps(self, obj: TOneOrMulti, many: bool = None, *args,
                  **kwargs) -> str:
            pass

        @typing.overload # type: ignore
        def load(self, data: typing.List[TEncoded],
                 many: bool = True, partial: bool = None,
                 unknown: str = None) -> \
                typing.List[A]:
            # ignore the mypy error of the decorator because mm does not define lists as an allowed input type
            pass

        @typing.overload
        def load(self, data: TEncoded,
                 many: None = None, partial: bool = None,
                 unknown: str = None) -> A:
            pass

        def load(self, data: TOneOrMultiEncoded,
                 many: bool = None, partial: bool = None,
                 unknown: str = None) -> TOneOrMulti:
            pass

        @typing.overload  # type: ignore
        def loads(self, json_data: JsonData,  # type: ignore
                  many: bool = True, partial: bool = None, unknown: str = None,
                  **kwargs) -> typing.List[A]:
            # ignore the mypy error of the decorator because mm does not define bytes as correct input data
            # mm has the wrong return type annotation (dict) so we can ignore the mypy error
            # for the return type overlap
            pass

        @typing.overload
        def loads(self, json_data: JsonData,
                  many: None = None, partial: bool = None, unknown: str = None,
                  **kwargs) -> A:
            pass

        def loads(self, json_data: JsonData,
                  many: bool = None, partial: bool = None, unknown: str = None,
                  **kwargs) -> TOneOrMulti:
            pass


    SchemaType = SchemaF[A]
else:
    SchemaType = Schema


def build_type(type_, options, mixin, field, cls):
    def inner(type_, options):
        while True:
            if not _is_new_type(type_):
                break

            type_ = type_.__supertype__

        if is_dataclass(type_):
            if _issubclass_safe(type_, mixin):
                options['field_many'] = bool(
                    _is_supported_generic(field.type) and _is_collection(
                        field.type))
                return fields.Nested(type_.schema(), **options)
            else:
                warnings.warn(f"Nested dataclass field {field.name} of type "
                              f"{field.type} detected in "
                              f"{cls.__name__} that is not an instance of "
                              f"dataclass_json. Did you mean to recursively "
                              f"serialize this field? If so, make sure to "
                              f"augment {type_} with either the "
                              f"`dataclass_json` decorator or mixin.")
                return fields.Field(**options)

        origin = getattr(type_, '__origin__', type_)
        args = [inner(a, {}) for a in getattr(type_, '__args__', []) if
                a is not type(None)]

        if origin in TYPES:
            return TYPES[origin](*args, **options)

        if _issubclass_safe(origin, Enum):
            return EnumField(enum=origin, by_value=True, *args, **options)

        if is_union_type(type_):
            union_types = [a for a in getattr(type_, '__args__', []) if
                           a is not type(None)]
            union_desc = dict(zip(union_types, args))
            return _UnionField(union_desc, cls, field, **options)

        warnings.warn(
            f"Unknown type {type_} at {cls.__name__}.{field.name}: {field.type} "
            f"It's advised to pass the correct marshmallow type to `mm_field`.")
        return fields.Field(**options)

    return inner(type_, options)


def schema(cls, mixin, infer_missing):
    schema = {}
    overrides = _user_overrides(cls)
    # TODO check the undefined parameters and add the proper schema action
    #  https://marshmallow.readthedocs.io/en/stable/quickstart.html
    for field in dc_fields(cls):
        metadata = (field.metadata or {}).get('dataclasses_json', {})
        metadata = overrides[field.name]
        if metadata.mm_field is not None:
            schema[field.name] = metadata.mm_field
        else:
            type_ = field.type
            options = {}
            missing_key = 'missing' if infer_missing else 'default'
            if field.default is not MISSING:
                options[missing_key] = field.default
            elif field.default_factory is not MISSING:
                options[missing_key] = field.default_factory

            if options.get(missing_key, ...) is None:
                options['allow_none'] = True

            if _is_optional(type_):
                options.setdefault(missing_key, None)
                options['allow_none'] = True
                if len(type_.__args__) == 2:
                    # Union[str, int, None] is optional too, but it has more than 1 typed field.
                    type_ = type_.__args__[0]

            if metadata.letter_case is not None:
                options['data_key'] = metadata.letter_case(field.name)

            t = build_type(type_, options, mixin, field, cls)
            # if type(t) is not fields.Field:  # If we use `isinstance` we would return nothing.
            if field.type != CatchAll:
                schema[field.name] = t

    return schema


def build_schema(cls: typing.Type[A],
                 mixin,
                 infer_missing,
                 partial) -> typing.Type[SchemaType]:
    Meta = type('Meta',
                (),
                {'fields': tuple(field.name for field in dc_fields(cls)
                                 if field.name != 'dataclass_json_config' and field.type != CatchAll)})

    @post_load
    def make_instance(self, kvs, **kwargs):
        return _decode_dataclass(cls, kvs, partial)

    def dumps(self, *args, **kwargs):
        if 'cls' not in kwargs:
            kwargs['cls'] = _ExtendedEncoder

        return Schema.dumps(self, *args, **kwargs)

    def dump(self, obj, *, many=None):
        dumped = Schema.dump(self, obj, many=many)
        # TODO This is hacky, but the other option I can think of is to generate a different schema
        #  depending on dump and load, which is even more hacky

        # The only problem is the catch all field, we can't statically create a schema for it
        # so we just update the dumped dict
        if many:
            for i, _obj in enumerate(obj):
                dumped[i].update(_handle_undefined_parameters_save(cls=_obj, kvs={}, usage="dump"))
        else:
            dumped.update(_handle_undefined_parameters_save(cls=obj, kvs={}, usage="dump"))
        return dumped

    schema_ = schema(cls, mixin, infer_missing)
    DataClassSchema: typing.Type[SchemaType] = type(
        f'{cls.__name__.capitalize()}Schema',
        (Schema,),
        {'Meta': Meta,
         f'make_{cls.__name__.lower()}': make_instance,
         'dumps': dumps,
         'dump': dump,
         **schema_})

    return DataClassSchema


class UndefinedParameterError(ValidationError):
    """
    Raised when something has gone wrong handling undefined parameters.
    """
    pass
