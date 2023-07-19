import json
from enum import Enum
from typing import Tuple

from dataclasses import dataclass

from dataclasses_json import dataclass_json


class MyEnum(Enum):
    STR1 = "str1"
    STR2 = "str2"
    STR3 = "str3"
    INT1 = 1
    FLOAT1 = 1.23


@dataclass_json
@dataclass
class DataWithHeterogeneousTuple:
    my_tuple: Tuple[MyEnum, str, float]


hetero_tuple_json = '{"my_tuple": ["str1", "str2", 1.23]}'
hetero_tuple_data = DataWithHeterogeneousTuple(my_tuple=(MyEnum.STR1, "str2", 1.23))


@dataclass_json
@dataclass
class DataWithNestedTuple:
    my_tuple: Tuple[Tuple[int, str], Tuple[MyEnum, int], int]


nested_tuple_json = '{"my_tuple": [[1, "str1"], ["str2", 1], 1]}'
nested_tuple_data = DataWithNestedTuple(my_tuple=((1, "str1"), (MyEnum.STR2, 1), 1))


@dataclass_json
@dataclass
class DataWithEllipsisTuple:
    my_tuple: Tuple[str, ...]


ellipsis_tuple_json = '{"my_tuple": ["str1", "str2", "str3"]}'
ellipsis_tuple_data = DataWithEllipsisTuple(my_tuple=("str1", "str2", "str3"))


class TestEncoder:
    def test_enum_with_tuple(self):
        assert hetero_tuple_data.to_json() == hetero_tuple_json, f'Actual: {hetero_tuple_data.to_json()}, Expected: {hetero_tuple_json}'
        assert hetero_tuple_data.to_dict(encode_json=True) == json.loads(hetero_tuple_json), f'Actual: {hetero_tuple_data.to_dict()}, Expected: {json.loads(hetero_tuple_json)}'

    def test_nested_tuple(self):
        assert nested_tuple_data.to_json() == nested_tuple_json, f'Actual: {nested_tuple_data.to_json()}, Expected: {nested_tuple_json}'
        assert nested_tuple_data.to_dict(encode_json=True) == json.loads(nested_tuple_json), f'Actual: {nested_tuple_data.to_dict()}, Expected: {json.loads(nested_tuple_json)}'

    def test_ellipsis_tuple(self):
        assert ellipsis_tuple_data.to_json() == ellipsis_tuple_json, f'Actual: {ellipsis_tuple_data.to_json()}, Expected: {ellipsis_tuple_json}'
        assert ellipsis_tuple_data.to_dict(encode_json=True) == json.loads(ellipsis_tuple_json), f'Actual: {ellipsis_tuple_data.to_dict()}, Expected: {json.loads(ellipsis_tuple_json)}'


class TestDecoder:
    def test_enum_with_tuple(self):
        tuple_data_from_json = DataWithHeterogeneousTuple.from_json(hetero_tuple_json)
        assert hetero_tuple_data == tuple_data_from_json
        assert tuple_data_from_json.to_json() == hetero_tuple_json

    def test_nested_tuple(self):
        tuple_data_from_json = DataWithNestedTuple.from_json(nested_tuple_json)
        assert nested_tuple_data == tuple_data_from_json
        assert tuple_data_from_json.to_json() == nested_tuple_json

    def test_ellipsis_tuple(self):
        tuple_data_from_json = DataWithEllipsisTuple.from_json(ellipsis_tuple_json)
        assert ellipsis_tuple_data == tuple_data_from_json
        assert tuple_data_from_json.to_json() == ellipsis_tuple_json
