from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

import pytest

from dataclasses_json import dataclass_json

S = TypeVar("S")
T = TypeVar("T")


@dataclass_json
@dataclass
class Bar:
    value: int


@dataclass_json
@dataclass
class Foo(Generic[T]):
    bar: T


@dataclass_json
@dataclass
class Baz(Generic[T]):
    foo: Foo[T]


@pytest.mark.parametrize(
    "instance_of_t, decodes_successfully",
    [
        pytest.param(1, True, id="literal"),
        pytest.param([1], True, id="literal_list"),
        pytest.param({"a": 1}, True, id="map_of_literal"),
        pytest.param(datetime(2021, 1, 1), False, id="extended_type"),
        pytest.param(Bar(1), False, id="object"),
    ]
)
def test_dataclass_with_generic_dataclass_field(instance_of_t, decodes_successfully):
    foo = Foo(bar=instance_of_t)
    baz = Baz(foo=foo)
    decoded = Baz[type(instance_of_t)].from_json(baz.to_json())
    assert decoded.foo == Foo.from_json(foo.to_json())
    if decodes_successfully:
        assert decoded == baz
    else:
        assert decoded != baz


@dataclass_json
@dataclass
class Foo2(Generic[T, S]):
    bar1: T
    bar2: S


@dataclass_json
@dataclass
class Baz2(Generic[T, S]):
    foo2: Foo2[T, S]


@pytest.mark.parametrize(
    "instance_of_t, decodes_successfully",
    [
        pytest.param(1, True, id="literal"),
        pytest.param([1], True, id="literal_list"),
        pytest.param({"a": 1}, True, id="map_of_literal"),
        pytest.param(datetime(2021, 1, 1), False, id="extended_type"),
        pytest.param(Bar(1), False, id="object"),
    ]
)
def test_dataclass_with_multiple_generic_dataclass_fields(instance_of_t, decodes_successfully):
    foo2 = Foo2(bar1=instance_of_t, bar2=instance_of_t)
    baz = Baz2(foo2=foo2)
    decoded = Baz2[type(instance_of_t), type(instance_of_t)].from_json(baz.to_json())
    assert decoded.foo2 == Foo2.from_json(foo2.to_json())
    if decodes_successfully:
        assert decoded == baz
    else:
        assert decoded != baz
