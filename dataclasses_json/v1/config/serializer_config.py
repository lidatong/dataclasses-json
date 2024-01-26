import functools
from enum import Enum
from pydoc import locate
from typing import Type, List, Dict

from dataclasses_json import LetterCase
from dataclasses_json.v1.serializers.default_json_serializer import JsonSerializer


class UndefinedFieldBehaviour(Enum):
    INCLUDE = "INCLUDE",
    IGNORE = "IGNORE",
    FAIL = "FAIL",


class SerializerConfig:
    undefined_fields: UndefinedFieldBehaviour
    letter_case: LetterCase
    serializers: List[str] = ["dataclasses_json.serializers.DefaultJsonSerializer"]

    @functools.cached_property
    def serializers(self) -> Dict[str, Type[JsonSerializer]]:
        def locate_serializer(name: str) -> Type[JsonSerializer]:
            matching_serializer = locate(name)
            if matching_serializer is None:
                raise ImportError(name=name)

        return {serializer_class: locate_serializer(serializer_class) for serializer_class in self.serializers}
