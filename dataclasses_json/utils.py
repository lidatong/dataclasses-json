import inspect
import sys
from datetime import datetime, timezone
from typing import Collection, Mapping, Optional


def _get_type_cons(type_):
    """More spaghetti logic for 3.6 vs. 3.7"""
    if sys.version_info.minor == 6:
        try:
            cons = type_.__extra__
        except AttributeError:
            try:
                cons = type_.__origin__
            except AttributeError:
                cons = type_
            else:
                cons = type_ if cons is None else cons
        else:
            try:
                cons = type_.__origin__ if cons is None else cons
            except AttributeError:
                cons = type_
    else:
        cons = type_.__origin__
    return cons


def _get_type_origin(type_):
    """Some spaghetti logic to accommodate differences between 3.6 and 3.7 in
    the typing api"""
    try:
        origin = type_.__origin__
    except AttributeError:
        if sys.version_info.minor == 6:
            try:
                origin = type_.__extra__
            except AttributeError:
                origin = type_
            else:
                origin = type_ if origin is None else origin
        else:
            origin = type_
    return origin


def _hasargs(type_, *args):
    try:
        res = all(arg in type_.__args__ for arg in args)
    except AttributeError:
        return False
    else:
        return res


def _isinstance_safe(o, t):
    try:
        result = isinstance(o, t)
    except Exception:
        return False
    else:
        return result


def _issubclass_safe(cls, classinfo):
    try:
        return issubclass(cls, classinfo)
    except Exception:
        return (_is_new_type_subclass_safe(cls, classinfo)
                if _is_new_type(cls)
                else False)


def _is_new_type_subclass_safe(cls, classinfo):
    super_type = getattr(cls, "__supertype__", None)

    if super_type:
        return _is_new_type_subclass_safe(super_type, classinfo)

    try:
        return issubclass(cls, classinfo)
    except Exception:
        return False


def _is_new_type(type_):
    return inspect.isfunction(type_) and hasattr(type_, "__supertype__")


def _is_optional(type_):
    return _issubclass_safe(type_, Optional) or _hasargs(type_, type(None))


def _is_mapping(type_):
    return _issubclass_safe(_get_type_origin(type_), Mapping)


def _is_collection(type_):
    return _issubclass_safe(_get_type_origin(type_), Collection)


def _is_nonstr_collection(type_):
    return (_issubclass_safe(_get_type_origin(type_), Collection)
            and not _issubclass_safe(type_, str))


def _timestamp_to_dt_aware(timestamp: float):
    tz = datetime.now(timezone.utc).astimezone().tzinfo
    dt = datetime.fromtimestamp(timestamp, tz=tz)
    return dt


def _undefined_parameter_action(cls):
    try:
        if cls.dataclass_json_config is None:
            return
        return cls.dataclass_json_config['undefined_parameters']
    except AttributeError:
        return


def _handle_undefined_parameters_save(cls, kvs, usage: str):
    """
    Checks if an undefined parameters action is defined and performs the according action.
    """
    undefined_parameter_action = _undefined_parameter_action(cls)
    if undefined_parameter_action is None:
        return kvs
    if usage.lower() == "from":
        return undefined_parameter_action.value.handle_from_dict(cls=cls, kvs=kvs)
    elif usage.lower() == "to":
        return undefined_parameter_action.value.handle_to_dict(obj=cls, kvs=kvs)
    elif usage.lower() == "dump":
        return undefined_parameter_action.value.handle_dump(obj=cls)
    else:
        raise ValueError(f"to_or_from must be one of ['to', 'from', 'dump'] (case-insensitive), but is '{usage}'")


class CatchAll:
    """
    Dummy type to indicate the catch all field.
    """
    pass