from dataclasses import dataclass
from typing import Generic, TypeVar

from dataclasses_json import dataclass_json

T = TypeVar("T")


@dataclass_json
@dataclass
class NestedClass(Generic[T]):
    value: T


@dataclass_json
@dataclass
class MyClass(Generic[T]):
    nested: NestedClass[T]


def test_dataclass_with_generic_dataclass_field():
    a = MyClass(nested=NestedClass(value="value"))
    assert MyClass.from_json(a.to_json()) == a
