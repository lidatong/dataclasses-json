from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict

import pytest
from pytest import mark, param


from dataclasses_json import DataClassJsonMixin


@dataclass(frozen=True)
class DataClassWithBuiltins(DataClassJsonMixin):
    actually_a_str: str
    actually_an_int: int
    actually_a_float: float
    actually_a_bool: bool


@mark.parametrize(
    "model_dict, expected_model",
    [
        param(
            {"actually_a_str": "str", "actually_an_int": 42, "actually_a_float": 42.1, "actually_a_bool": True},
            DataClassWithBuiltins(actually_a_str="str", actually_an_int=42, actually_a_float=42.1, actually_a_bool=True),
            id="Happy case"
        ),
        param(
            {"actually_a_str": "str", "actually_an_int": Decimal("42.1"), "actually_a_float": Decimal("42.1"), "actually_a_bool": True },
            DataClassWithBuiltins(actually_a_str="str", actually_an_int=42, actually_a_float=42.1, actually_a_bool=True),
            id="Decimal as int and float"
        ),
        param(
            {"actually_a_str": "str", "actually_an_int": 42, "actually_a_float": 42.1, "actually_a_bool": "False"},
            DataClassWithBuiltins(actually_a_str="str", actually_an_int=42, actually_a_float=42.1,
                                  actually_a_bool=False),
            id="Bool passed as a valid string"
        ),
        param(
            {"actually_a_str": "str", "actually_an_int": 42, "actually_a_float": 42.1, "actually_a_bool": 1},
            DataClassWithBuiltins(actually_a_str="str", actually_an_int=42, actually_a_float=42.1,
                                  actually_a_bool=True),
            id="Bool passed using valid discrete integer range [0,1]"
        ),
    ]
)
def test_dataclass_with_implicit_builtins(model_dict: Dict, expected_model: DataClassWithBuiltins):
    assert DataClassWithBuiltins.from_dict(model_dict) == expected_model


@mark.parametrize(
    "model_dict",
    [
        param(
            {"actually_a_str": "str", "actually_an_int": 42, "actually_a_float": 42.1, "actually_a_bool": 1234},
            id="Bool passed using valid discrete integer range [0,1]"
        ),
        param(
            {"actually_a_str": "str", "actually_an_int": 42, "actually_a_float": 42.1, "actually_a_bool": "0"},
            id="Bool passed using a string rather than an integer or a boolean string"
        ),
    ]
)
def test_dataclass_with_implicit_builtins_failed_bool(model_dict: Dict):
    with pytest.raises(ValueError):
        DataClassWithBuiltins.from_dict(model_dict)
