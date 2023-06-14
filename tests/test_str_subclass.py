from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin


class MyStr(str):

    def is_even_length(self) -> bool:
        return len(self) % 2 == 0


@dataclass(frozen=True)
class DataClassWithStrSubclass(DataClassJsonMixin):
    any_str: str
    my_str: MyStr


class TestDataClassWithStrSubclass:

    def test_encode__no_instantiation_required(self):
        model_dict = {"any_str": "str", "my_str": MyStr("str")}
        expected = DataClassWithStrSubclass(any_str="str", my_str=MyStr("str"))
        actual = DataClassWithStrSubclass.from_dict(model_dict)
        assert expected == actual
        assert model_dict["my_str"] is actual.my_str

    def test_encode__subclass_str_instantiated(self):
        model_dict = {"any_str": "str", "my_str": "str"}
        expected = DataClassWithStrSubclass(any_str="str", my_str=MyStr("str"))
        actual = DataClassWithStrSubclass.from_dict(model_dict)
        assert expected == actual
        assert model_dict["my_str"] is not actual.my_str