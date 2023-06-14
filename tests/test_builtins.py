from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from pytest import mark, param


from dataclasses_json import DataClassJsonMixin


@dataclass(frozen=True)
class DataClassWithBuiltins(DataClassJsonMixin):
    actually_a_str: str
    actually_an_int: int
    actually_a_float: float


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
