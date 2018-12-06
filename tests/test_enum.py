from enum import Enum
from typing import Dict, List

from dataclasses import dataclass

from dataclasses_json import dataclass_json


class MyEnum(Enum):
    STR1 = "str1"
    STR2 = "str2"
    STR3 = "str3"
    INT1 = 1
    FLOAT1 = 1.23


@dataclass_json
@dataclass(frozen=True)
class DataWithEnum:
    name: str
    my_enum: MyEnum = MyEnum.STR3


d1 = DataWithEnum('name1', MyEnum.STR1)
d1_json = '{"name": "name1", "my_enum": "str1"}'

# Make sure the enum is set to the default value defined by MyEnum
d2_using_default_value = DataWithEnum('name2')
d2_json = '{"name": "name2", "my_enum": "str3"}'

d3_int = DataWithEnum('name1', MyEnum.INT1)
d3_int_json = '{"name": "name1", "my_enum": 1}'
d4_float = DataWithEnum('name1', MyEnum.FLOAT1)
d4_float_json = '{"name": "name1", "my_enum": 1.23}'


@dataclass_json
@dataclass(frozen=True)
class EnumContainer:
    enum_list: List[MyEnum]
    dict_enum_value: Dict[str, MyEnum]


container_json = '{"enum_list": ["str3", 1], "dict_enum_value": {"key1str": "str1", "key1float": 1.23}}'
container = EnumContainer(
    enum_list=[MyEnum.STR3, MyEnum.INT1],
    dict_enum_value={"key1str": MyEnum.STR1, "key1float": MyEnum.FLOAT1})


class TestEncoder:
    def test_data_with_enum(self):
        assert d1.to_json() == d1_json, f'Actual: {d1.to_json()}, Expected: {d1_json}'
        assert d3_int.to_json() == d3_int_json, f'Actual: {d3_int.to_json()}, Expected: {d3_int_json}'
        assert d4_float.to_json() == d4_float_json, f'Actual: {d4_float.to_json()}, Expected: {d4_float_json}'

    def test_data_with_enum_default_value(self):
        d2_to_json = d2_using_default_value.to_json()
        assert d2_to_json == d2_json, f"A default value was not included in the JSON encode. " \
                                      f"Expected: {d2_json}, Actual: {d2_to_json}"

    def test_collection_with_enum(self):
        assert container.to_json() == container_json


class TestDecoder:
    def test_data_with_enum(self):
        d1_from_json = DataWithEnum.from_json(d1_json)
        assert d1 == d1_from_json
        assert d1_from_json.to_json() == d1_json

        d3_int_from_json = DataWithEnum.from_json(d3_int_json)
        assert d3_int == d3_int_from_json
        assert d3_int_from_json.to_json() == d3_int_json

        d4_float_from_json = DataWithEnum.from_json(d4_float_json)
        assert d4_float == d4_float_from_json
        assert d4_float_from_json.to_json() == d4_float_json

    def test_data_with_enum_default_value(self):
        d2_from_json = DataWithEnum.from_json(d2_json)
        assert d2_using_default_value == d2_from_json
        json_from_d2 = d2_from_json.to_json()
        assert json_from_d2 == d2_json, f"A default value was not included in the JSON encode. " \
                                        f"Expected: {d2_json}, Actual: {json_from_d2}"

    def test_collection_with_enum(self):
        container_from_json = EnumContainer.from_json(container_json)
        assert container == container_from_json
        assert container_from_json.to_json() == container_json
