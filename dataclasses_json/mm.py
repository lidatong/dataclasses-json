import warnings
from dataclasses import MISSING, is_dataclass
from datetime import datetime
from uuid import UUID

from marshmallow import fields

from dataclasses_json.core import _is_supported_generic
from dataclasses_json.utils import (_is_collection, _is_mapping,
                                    _is_nonstr_collection, _is_optional,
                                    _issubclass_safe, _timestamp_to_dt_aware)


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


_type_to_cons = {
    dict: fields.Dict,
    list: fields.List,
    str: fields.Str,
    int: fields.Int,
    float: fields.Float,
    bool: fields.Bool,
    datetime: _TimestampField,
    UUID: fields.UUID
}


def _make_nested_fields(fields_, dataclass_json_cls, infer_missing):
    nested_fields = {}
    for field, type_, field_many in _inspect_nested_fields(fields_):
        if _issubclass_safe(type_, dataclass_json_cls):
            if infer_missing and _is_optional(field.type):
                schema = fields.Nested(type_.schema(),
                                       many=field_many,
                                       missing=None)
            else:
                schema = fields.Nested(type_.schema(),
                                       many=field_many)
            nested_fields[field.name] = schema
        else:
            warnings.warn(f"Nested dataclass field {field.name} of type "
                          f"{field.type} detected in "
                          f"{dataclass_json_cls.__name__} that is not an instance of "
                          f"dataclass_json. Did you mean to recursively "
                          f"serialize this field? If so, make sure to "
                          f"augment {field.type} with either the "
                          f"`dataclass_json` decorator or mixin.")
    return nested_fields


def _inspect_nested_fields(fields_):
    nested_dc_fields_and_is_many = []
    for field in fields_:
        if _is_supported_generic(field.type):
            t_arg = field.type.__args__[0]
            if is_dataclass(t_arg):
                if _is_collection(field.type):
                    nested_dc_fields_and_is_many.append((field, t_arg, True))
                else:
                    nested_dc_fields_and_is_many.append((field, t_arg, False))
        elif is_dataclass(field.type):
            nested_dc_fields_and_is_many.append((field, field.type, False))
    return nested_dc_fields_and_is_many


def _make_default_fields(fields_, cls, infer_missing):
    default_fields = {}
    for field in fields_:
        if field.default is not MISSING:
            default_fields[field.name] = _make_default_field(field.type,
                                                             field.default,
                                                             cls)
        elif field.default_factory is not MISSING:
            default_fields[field.name] = _make_default_field(field.type,
                                                             field.default_factory,
                                                             cls)
        elif _is_optional(field.type) and infer_missing:
            default_fields[field.name] = _make_default_field(field.type,
                                                             None,
                                                             cls)
    return default_fields


def _make_default_field(type_, default, cls):
    cons_type = type_
    cons_type = (list if _is_nonstr_collection(cons_type) else cons_type)
    cons_type = (dict if _is_mapping(cons_type) else cons_type)
    cons_type = (type_.__args__[0] if _is_optional(cons_type) else cons_type)
    cons = _type_to_cons[cons_type]
    if cons is fields.List:
        type_arg = type_.__args__[0]
        if type_arg not in _type_to_cons:
            raise TypeError(f"Unsupported {type_arg} detected. Is it "
                            f"a supported JSON type or dataclass_json "
                            f"instance?")
        arg_cons = _type_to_cons[type_arg]
        return cons(arg_cons, missing=default)
    return cons(missing=default)


import typing
from dataclasses import fields as dc_fields
from marshmallow import Schema, post_load
from dataclasses_json.core import _decode_dataclass


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
    UUID: fields.UUID
}

def build_type(type_, options, mixin, field, cls):
    def inner(type_, options):
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
        warnings.warn(f"Unknown type {type_} at {cls.__name__}.{field.name}: {field.type} "
                      f"It's advised to pass the correct marshmallow type to `mm_field`.")
        return field.Field(**options)
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

    schema_ = schema(cls, mixin, infer_missing)
    DataClassSchema = type(f'{cls.__name__.capitalize()}Schema',
                           (Schema,),
                           {'Meta': Meta,
                            f'make_{cls.__name__.lower()}': make_instance,
                            **schema_})

    return DataClassSchema
