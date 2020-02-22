import json
import warnings
from typing import (Callable, Dict)


class GlobalConfig:
    _disable_msg = "You can capture all warnings with logging.captureWarnings."

    def __init__(self):
        self._suppress_warnings: bool = False
        self.encoders: Dict[type, Callable] = {}
        self.decoders: Dict[type, Callable] = {}
        self._json_module = json

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


global_config = GlobalConfig()
