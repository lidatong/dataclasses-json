from dataclasses import dataclass
from decimal import Decimal

from pytest import mark, param


from dataclasses_json import DataClassJsonMixin


@dataclass(frozen=True)
class DataClassWithBuiltins(DataClassJsonMixin):
    actually_a_str: str
    actually_an_int: int
    actually_a_float: float


class StrSubclass(str):
    pass


@dataclass
class DataClassWithBuiltinCollection(DataClassJsonMixin):
    things: list[StrSubclass]


@mark.parametrize(
    "model_dict, expected_model",
    [
        param(
            {"actually_a_str": "str", "actually_an_int": 42, "actually_a_float": 42.1},
            DataClassWithBuiltins(actually_a_str="str", actually_an_int=42, actually_a_float=42.1),
            id="Happy case"
        ),
        param(
            {"actually_a_str": "str", "actually_an_int": Decimal("42.1"), "actually_a_float": Decimal("42.1")},
            DataClassWithBuiltins(actually_a_str="str", actually_an_int=42, actually_a_float=42.1),
            id="Decimal as int and float"
        ),
    ]
)
def test__DataClassWithBuiltins__from_dict(model_dict, expected_model):
    assert DataClassWithBuiltins.from_dict(model_dict) == expected_model


@mark.parametrize(
    "serialized_model, expected_model",
    [
        param(
            '{"things": ["John Doe"]}',
            DataClassWithBuiltinCollection(things=[StrSubclass("John Doe")]),
            id="Collection of str subclasses"
        ),
        param(
            '{"things": []}',
            DataClassWithBuiltinCollection(things=[]),
            id="Empty collection of str subclasses"
        ),
    ]
)
def test_builtins_collections_with_subclass(serialized_model: str, expected_model: DataClassWithBuiltinCollection):
    deser = DataClassWithBuiltinCollection.from_json(serialized_model)
    if len(deser.things) > 0:
        assert isinstance(deser.things[0], StrSubclass)
    # for empty list we just assert there is no exception
