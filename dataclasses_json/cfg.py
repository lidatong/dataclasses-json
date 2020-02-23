import functools
from typing import (Callable, Dict, Optional, Union)

from marshmallow.fields import Field as MarshmallowField

from dataclasses_json.undefined import Undefined, UndefinedParameterError


# TODO: add warnings?
class _GlobalConfig:

    def __init__(self):
        self.encoders: Dict[type, Callable] = {}
        self.decoders: Dict[type, Callable] = {}
        # self._json_module = json

    # TODO: #180
    # @property
    # def json_module(self):
    #     return self._json_module
    #
    # @json_module.setter
    # def json_module(self, value):
    #     warnings.warn(f"Now using {value.__name__} module to handle JSON. "
    #                   f"{self._disable_msg}")
    #     self._json_module = value


global_config = _GlobalConfig()


def config(metadata: dict = None, *,
           encoder: Callable = None,
           decoder: Callable = None,
           mm_field: MarshmallowField = None,
           letter_case: Callable[[str], str] = None,
           undefined: Optional[Union[str, Undefined]] = None,
           field_name: str = None) -> Dict[str, dict]:
    if metadata is None:
        metadata = {}

    lib_metadata = metadata.setdefault('dataclasses_json', {})

    if encoder is not None:
        lib_metadata['encoder'] = encoder

    if decoder is not None:
        lib_metadata['decoder'] = decoder

    if mm_field is not None:
        lib_metadata['mm_field'] = mm_field

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
        lib_metadata['letter_case'] = letter_case

    if undefined is not None:
        # Get the corresponding action for undefined parameters
        if isinstance(undefined, str):
            if not hasattr(Undefined, undefined.upper()):
                valid_actions = list(action.name for action in Undefined)
                raise UndefinedParameterError(
                    f"Invalid undefined parameter action, "
                    f"must be one of {valid_actions}")
            undefined = Undefined[undefined.upper()]

        lib_metadata['undefined'] = undefined

    return metadata
