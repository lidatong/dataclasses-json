import typing
import warnings

from dataclasses import MISSING, is_dataclass, fields as dc_fields
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum

from marshmallow import fields, Schema, post_load
from marshmallow_enum import EnumField

from dataclasses_json.core import (_is_supported_generic, _decode_dataclass,
                                   _ExtendedEncoder)
from dataclasses_json.utils import (_is_collection, _is_optional,
                                    _issubclass_safe, _timestamp_to_dt_aware,
                                    _is_new_type)


class _TimestampField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return value.timestamp()

    def _deserialize(self, value, attr, data, **kwargs):
        return _timestamp_to_dt_aware(value)


class _IsoField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return value.isoformat()

    def _deserialize(self, value, attr, data, **kwargs):
        return datetime.fromisoformat(value)


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
    Decimal: fields.Decimal
}


def build_type(type_, options, mixin, field, cls):
    def inner(type_, options):
        while True:
            if not _is_new_type(type_):
                break

            type_ = type_.__supertype__

        if is_dataclass(type_):
            if _issubclass_safe(type_, mixin):
                options['field_many'] = bool(_is_supported_generic(field.type) and _is_collection(field.type))
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
        args = [inner(a, {}) for a in getattr(type_, '__args__', [])]

        if origin in TYPES:
            return TYPES[origin](*args, **options)

        if _issubclass_safe(origin, Enum):
            return EnumField(enum=origin, by_value=True, *args, **options)

        warnings.warn(f"Unknown type {type_} at {cls.__name__}.{field.name}: {field.type} "
                      f"It's advised to pass the correct marshmallow type to `mm_field`.")
        return fields.Field(**options)
    return inner(type_, options)


def schema(cls, mixin, infer_missing):
    schema = {}
    for field in dc_fields(cls):
        if 'dataclasses_json' in (field.metadata or {}):
            schema[field.name] = field.metadata['dataclasses_json'].get('mm_field')
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
                type_ = type_.__args__[0]
                options['allow_none'] = True

            t = build_type(type_, options, mixin, field, cls)
            #if type(t) is not fields.Field:  # If we use `isinstance` we would return nothing.
            schema[field.name] = t
    return schema


def build_schema(cls, mixin, infer_missing, partial):
    Meta = type('Meta',
                (),
                {'fields': tuple(field.name for field in dc_fields(cls))})

    @post_load
    def make_instance(self, kvs):
        return _decode_dataclass(cls, kvs, partial)

    def dumps(self, *args, **kwargs):
        if 'cls' not in kwargs:
            kwargs['cls'] = _ExtendedEncoder

        return Schema.dumps(self, *args, **kwargs)

    schema_ = schema(cls, mixin, infer_missing)
    DataClassSchema = type(f'{cls.__name__.capitalize()}Schema',
                           (Schema,),
                           {'Meta': Meta,
                            f'make_{cls.__name__.lower()}': make_instance,
                            'dumps': dumps,
                            **schema_})

    return DataClassSchema
