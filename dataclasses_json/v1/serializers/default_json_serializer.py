from abc import ABC, abstractmethod
from typing import Type, TypeVar, Dict

TClass = TypeVar("TClass")


class JsonSerializer(ABC):
    def __init__(self, class_to_serialize: Type[TClass]):
        self._class_to_serialize = class_to_serialize

    @abstractmethod
    def to_json(self) -> str:
        """

        """

    @abstractmethod
    def from_json(self, value: str) -> TClass:
        """

        """

    @abstractmethod
    def to_dict(self) -> Dict:
        """

        """

    @abstractmethod
    def from_dict(self, value: Dict) -> TClass:
        """

        """


class DefaultJsonSerializer(JsonSerializer):

    def to_json(self) -> str:
        pass

    def from_json(self, value: str) -> TClass:
        pass

    def to_dict(self) -> Dict:
        pass

    def from_dict(self, value: Dict) -> TClass:
        pass
