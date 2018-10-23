import json
import warnings
from dataclasses import MISSING, fields, is_dataclass
from typing import Collection

from dataclasses_json.utils import (_get_type_cons, _get_type_origin,
                                    _is_collection, _is_optional,
                                    _isinstance_safe, _issubclass_safe)


class _CollectionEncoder(json.JSONEncoder):
    def default(self, o):
        if _isinstance_safe(o, Collection):
            return list(o)
        return json.JSONEncoder.default(self, o)


def _decode_dataclass(cls, kvs, infer_missing):
    kvs = {} if kvs is None and infer_missing else kvs
    # print(kvs)
    # print({field for field in fields(cls) if field.name not in kvs})
    missing_fields = {field for field in fields(cls) if field.name not in kvs}
    for field in missing_fields:
        if field.default is not MISSING:
            kvs[field.name] = field.default
        elif infer_missing:
            kvs[field.name] = None

    init_kwargs = {}
    for field in fields(cls):
        field_value = kvs[field.name]
        if field_value is None and not _is_optional(field.type):
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
        elif is_dataclass(field.type):
            # FIXME this is a band-aid to deal with the value already being
            # serialized when handling nested marshmallow schema
            # proper fix is to investigate the marshmallow schema generation
            # code
            if is_dataclass(field_value):
                value = field_value
            else:
                value = _decode_dataclass(field.type,
                                          field_value,
                                          infer_missing)
            init_kwargs[field.name] = value

        elif _is_supported_generic(field.type) and field.type != str:
            init_kwargs[field.name] = _decode_generic(field.type,
                                                      field_value,
                                                      infer_missing)
        else:
            init_kwargs[field.name] = field_value
    return cls(**init_kwargs)


def _is_supported_generic(type_):
    not_str = not _issubclass_safe(type_, str)
    return (not_str and _is_collection(type_)) or _is_optional(type_)


def _decode_generic(type_, value, infer_missing):
    if value is None:
        res = value
    elif _issubclass_safe(_get_type_origin(type_), Collection):
        # this is a tricky situation where we need to check both the annotated
        # type info (which is usually a type from `typing`) and check the
        # value's type directly using `type()`.
        #
        # if the type_arg is a generic we can use the annotated type, but if the
        # type_arg is a typevar we need to extract the reified type information
        # hence the check of `is_dataclass(value)`
        type_arg = type_.__args__[0]
        if is_dataclass(type_arg) or is_dataclass(value):
            xs = (_decode_dataclass(type_arg, v, infer_missing) for v in value)
        elif _is_supported_generic(type_arg):
            xs = (_decode_generic(type_arg, v, infer_missing) for v in value)
        else:
            xs = value
        # get the constructor if using corresponding generic type in `typing`
        # otherwise fallback on the type returned by
        try:
            res = _get_type_cons(type_)(xs)
        except TypeError:
            res = type_(xs)
    else:  # Optional
        type_arg = type_.__args__[0]
        if is_dataclass(type_arg) or is_dataclass(value):
            res = _decode_dataclass(type_arg, value, infer_missing)
        elif _is_supported_generic(type_arg):
            res = _decode_generic(type_arg, value, infer_missing)
        else:
            res = value
    return res


def _nested_fields(fields):
    nested_dc_fields_and_is_many = []
    for field in fields:
        if _is_supported_generic(field.type):
            type_arg = field.type.__args__[0]
            if is_dataclass(type_arg):
                if _is_collection(field.type):
                    nested_dc_fields_and_is_many.append((field, True))
                else:
                    nested_dc_fields_and_is_many.append((field, False))
        elif is_dataclass(field.type):
            nested_dc_fields_and_is_many.append((field, False))
    return nested_dc_fields_and_is_many
