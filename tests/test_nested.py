from tests.entities import (DataClassWithDataClass,
                            DataClassWithList,
                            DataClassX,
                            DataClassXs,
                            DataClassWithNestedCustomEncoder,
                            DataClassWithCustomEncoder)


class TestEncoder:
    def test_nested_dataclass(self):
        assert (DataClassWithDataClass(DataClassWithList([1])).to_json() ==
                '{"dc_with_list": {"xs": [1]}}')

    def test_nested_list_of_dataclasses(self):
        assert (DataClassXs([DataClassX(0), DataClassX(1)]).to_json() ==
                '{"xs": [{"x": 0}, {"x": 1}]}')

    def test_nested_custom_encoded_dataclass(self):
        assert (DataClassWithNestedCustomEncoder(DataClassWithCustomEncoder(1, None))).to_json() == '{"a": {"a": 1}}'


class TestDecoder:
    def test_nested_dataclass(self):
        assert (DataClassWithDataClass.from_json(
            '{"dc_with_list": {"xs": [1]}}') ==
                DataClassWithDataClass(DataClassWithList([1])))

    def test_nested_list_of_dataclasses(self):
        assert (DataClassXs.from_json('{"xs": [{"x": 0}, {"x": 1}]}') ==
                DataClassXs([DataClassX(0), DataClassX(1)]))

    def test_nested_custom_encoded_dataclass(self):
        assert (DataClassWithNestedCustomEncoder.from_json('{"a": {"a": 1}}') ==
                DataClassWithNestedCustomEncoder(DataClassWithCustomEncoder(1, None)))
