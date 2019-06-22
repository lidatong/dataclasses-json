import copy
import json
import warnings
from collections import namedtuple
from dataclasses import MISSING, _is_dataclass_instance, fields, is_dataclass, asdict
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Collection, Mapping, Union, get_type_hints
from typing_inspect import is_union_type
from uuid import UUID

from dataclasses_json.utils import (
    _get_type_cons,
    _is_collection,
    _is_mapping,
    _is_new_type,
    _is_optional,
    _isinstance_safe,
    _issubclass_safe)

Json = Union[dict, list, str, int, float, bool, None]


class _ExtendedEncoder(json.JSONEncoder):
    def default(self, o) -> Json:
        result: Json
        if _isinstance_safe(o, Collection):
            if _isinstance_safe(o, Mapping):
                result = dict(o)
            else:
                result = list(o)
        elif _isinstance_safe(o, datetime):
            result = o.timestamp()
        elif _isinstance_safe(o, UUID):
            result = str(o)
        elif _isinstance_safe(o, Enum):
            result = o.value
        elif _isinstance_safe(o, Decimal):
            result = str(o)
        else:
            result = json.JSONEncoder.default(self, o)
        return result


def _overrides(dc):
    overrides = {}
    attrs = ['encoder', 'decoder', 'mm_field']
    FieldOverride = namedtuple('FieldOverride', attrs)
    for field in fields(dc):
        # if the field has dataclasses_json metadata, we cons a FieldOverride
        # so there's a distinction between FieldOverride with all Nones
        # and field that just doesn't appear in overrides
        if field.metadata is not None and 'dataclasses_json' in field.metadata:
            metadata = field.metadata['dataclasses_json']
            overrides[field.name] = FieldOverride(*map(metadata.get, attrs))
    return overrides


def _override(kvs, overrides, attr):
    override_kvs = {}
    for k, v in kvs.items():
        if k in overrides and getattr(overrides[k], attr) is not None:
            override_kvs[k] = getattr(overrides[k], attr)(v)
        else:
            override_kvs[k] = v
    return override_kvs


def _decode_dataclass(cls, kvs, infer_missing):
    if isinstance(kvs, cls):
        return kvs
    overrides = _overrides(cls)
    kvs = {} if kvs is None and infer_missing else kvs
    missing_fields = {field for field in fields(cls) if field.name not in kvs}
    for field in missing_fields:
        if field.default is not MISSING:
            kvs[field.name] = field.default
        elif field.default_factory is not MISSING:
            kvs[field.name] = field.default_factory()
        elif infer_missing:
            kvs[field.name] = None

    init_kwargs = {}
    types = get_type_hints(cls)
    for field in fields(cls):
        # The field should be skipped from being added
        # to init_kwargs as it's not intended as a constructor argument.
        if not field.init:
            continue

        field_value = kvs[field.name]
        field_type = types[field.name]
        if field_value is None and not _is_optional(field_type):
            warning = (f"value of non-optional type {field.name} detected "
                       f"when decoding {cls.__name__}")
            if infer_missing:
                warnings.warn(
                    f"Missing {warning} and was defaulted to None by "
                    f"infer_missing=True. "
                    f"Set infer_missing=False (the default) to prevent this "
                    f"behavior.", RuntimeWarning)
            else:
                warnings.warn(f"`NoneType` object {warning}.", RuntimeWarning)
            init_kwargs[field.name] = field_value
            continue

        while True:
            if not _is_new_type(field_type):
                break

            field_type = field_type.__supertype__

        if (field.name in overrides
              and overrides[field.name].decoder is not None):
            # FIXME hack
            if field_type is type(field_value):
                init_kwargs[field.name] = field_value
            else:
                init_kwargs[field.name] = overrides[field.name].decoder(
                    field_value)
        elif is_dataclass(field_type):
            # FIXME this is a band-aid to deal with the value already being
            # serialized when handling nested marshmallow schema
            # proper fix is to investigate the marshmallow schema generation
            # code
            if is_dataclass(field_value):
                value = field_value
            else:
                value = _decode_dataclass(field_type, field_value,
                                          infer_missing)
            init_kwargs[field.name] = value
        elif _is_supported_generic(field_type) and field_type != str:
            init_kwargs[field.name] = _decode_generic(field_type,
                                                      field_value,
                                                      infer_missing)
        elif _issubclass_safe(field_type, datetime):
            # FIXME this is a hack to deal with mm already decoding
            # the issue is we want to leverage mm fields' missing argument
            # but need this for the object creation hook
            if isinstance(field_value, datetime):
                dt = field_value
            else:
                tz = datetime.now(timezone.utc).astimezone().tzinfo
                dt = datetime.fromtimestamp(field_value, tz=tz)
            init_kwargs[field.name] = dt
        elif _issubclass_safe(field_type, Decimal):
            init_kwargs[field.name] = (field_value
                                       if isinstance(field_value, Decimal)
                                       else Decimal(field_value))
        elif _issubclass_safe(field_type, UUID):
            init_kwargs[field.name] = (field_value
                                       if isinstance(field_value, UUID)
                                       else UUID(field_value))
        else:
            init_kwargs[field.name] = field_value
    return cls(**init_kwargs)


def _is_supported_generic(type_):
    not_str = not _issubclass_safe(type_, str)
    is_enum = _issubclass_safe(type_, Enum)
    return (not_str and _is_collection(type_)) or _is_optional(type_) or is_union_type(type_) or is_enum


def _decode_generic(type_, value, infer_missing):
    if value is None:
        res = value
    elif _issubclass_safe(type_, Enum):
        # Convert to an Enum using the type as a constructor. Assumes a direct match is found.
        res = type_(value)
    elif _is_collection(type_):
        if _is_mapping(type_):
            k_type, v_type = type_.__args__
            # a mapping type has `.keys()` and `.values()` (see collections.abc)
            ks = _decode_dict_keys(k_type, value.keys(), infer_missing)
            vs = _decode_items(v_type, value.values(), infer_missing)
            xs = zip(ks, vs)
        else:
            xs = _decode_items(type_.__args__[0], value, infer_missing)

        # get the constructor if using corresponding generic type in `typing`
        # otherwise fallback on constructing using type_ itself
        try:
            res = _get_type_cons(type_)(xs)
        except TypeError:
            res = type_(xs)
    else:  # Optional or Union
        if _is_optional(type_) and len(type_.__args__) == 2:  # Optional
            type_arg = type_.__args__[0]
            if is_dataclass(type_arg) or is_dataclass(value):
                res = _decode_dataclass(type_arg, value, infer_missing)
            elif _is_supported_generic(type_arg):
                res = _decode_generic(type_arg, value, infer_missing)
            else:
                res = value
        else:  # Union (already decoded or unsupported 'from_json' used)
            res = value
    return res


def _decode_dict_keys(key_type, xs, infer_missing):
    """
    Because JSON object keys must be strs, we need the extra step of decoding
    them back into the user's chosen python type
    """
    # handle NoneType keys... it's weird to type a Dict as NoneType keys
    # but it's valid...
    key_type = (lambda x: x) if key_type is type(None) else key_type
    return map(key_type, _decode_items(key_type, xs, infer_missing))


def _decode_items(type_arg, xs, infer_missing):
    """
    This is a tricky situation where we need to check both the annotated
    type info (which is usually a type from `typing`) and check the
    value's type directly using `type()`.

    If the type_arg is a generic we can use the annotated type, but if the
    type_arg is a typevar we need to extract the reified type information
    hence the check of `is_dataclass(vs)`
    """
    if is_dataclass(type_arg) or is_dataclass(xs):
        items = (_decode_dataclass(type_arg, x, infer_missing)
                 for x in xs)
    elif _is_supported_generic(type_arg):
        items = (_decode_generic(type_arg, x, infer_missing) for x in xs)
    else:
        items = xs
    return items


def _asdict(obj):
    """
    A re-implementation of `asdict` (based on the original in the `dataclasses`
    source) to support arbitrary Collection and Mapping types.
    """
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _asdict(getattr(obj, f.name))
            result.append((f.name, value))
        return _override(dict(result), _overrides(obj), 'encoder')
    elif isinstance(obj, Mapping):
        return dict((_asdict(k), _asdict(v)) for k, v in obj.items())
    elif isinstance(obj, Collection) and not isinstance(obj, str):
        return list(_asdict(v) for v in obj)
    else:
        return copy.deepcopy(obj)
