import sys
from typing import Callable, Dict

from marshmallow import fields

_callable_to_alias_map = dict()
_alias_to_callable_map = dict()


def function_alias(alias: str):
    """
    Decorator factory to add a function to the alias <-> callable maps.
    :param alias: Alias for the decorated function.
    :return: Decorator
    """

    def function_alias_decorator(function: Callable[[Dict], Dict]):
        """
        Add the function to the alias <-> function map.
        :param function: Decorated function to map.
        :return: Decorated function.
        """
        if alias in _alias_to_callable_map:
            raise KeyError(f"Function alias '{alias}' already mapped.")
        _callable_to_alias_map[function] = alias
        _alias_to_callable_map[alias] = function
        return function

    return function_alias_decorator


def method_alias(alias: str):
    """
    Decorator factory to add a method to the alias <-> callable maps.
    :param alias: Alias for the decorated method.
    :return: Decorator
    """

    def method_alias_decorator(method: Callable[[Dict], Dict]):
        """
        Add the method to the alias <-> function map.
        :param method: Decorated method to map.
        :return: Decorated function.
        """
        key = method_key(method)
        if alias in _alias_to_callable_map:
            raise KeyError(f"Method alias '{alias}' already mapped.")
        _callable_to_alias_map[key] = alias
        _alias_to_callable_map[alias] = key
        return method

    return method_alias_decorator


def method_key(method: Callable) -> str:
    """Fully qualified class name module.class.method"""
    return f"{method.__module__}.{method.__qualname__}"


class AliasedFunctionField(fields.Field):
    """
    Serializer to convert the function field to it's string representation for serialization.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        return _callable_to_alias_map[value]

    @staticmethod
    def encoder(*args, **kwargs):
        return _callable_to_alias_map[args[0]]

    @staticmethod
    def decoder(*args, **kwargs):
        return _alias_to_callable_map[args[0]]


aliased_function_field = {
    "dataclasses_json": {
        "encoder": AliasedFunctionField.encoder,
        "decoder": AliasedFunctionField.decoder,
        "mm_field": AliasedFunctionField(),
    }
}


class AliasedMethodField(fields.Field):
    """
    Serializer to convert the method field to it's string representation for serialization.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        return _callable_to_alias_map[method_key(value)]

    def _deserialize(self, value, attr, data, **kwargs):
        key = _alias_to_callable_map[value]
        module, cls, method = key.rsplit(".", 2)
        obj = getattr(sys.modules[module], cls)(**kwargs)
        return getattr(obj, method)

    @staticmethod
    def encoder(*args, **kwargs):
        return _callable_to_alias_map[method_key(args[0])]

    @staticmethod
    def decoder(*args, **kwargs):
        # Check to see if the object has already been decoded and just return it.
        if not isinstance(args[0], str):
            return args[0]
        key = _alias_to_callable_map[args[0]]
        module, cls, method = key.rsplit(".", 2)
        obj = getattr(sys.modules[module], cls)(**kwargs)
        return getattr(obj, method)


aliased_method_field = {
    "dataclasses_json": {
        "encoder": AliasedMethodField.encoder,
        "decoder": AliasedMethodField.decoder,
        "mm_field": AliasedMethodField(),
    }
}
