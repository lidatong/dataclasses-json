from tests.entities import (DataClassWithDataClass,
                            DataClassWithList,
                            DataClassX,
                            DataClassXs)


class TestEncoder:
    def test_nested_dataclass(self):
        assert (DataClassWithDataClass(DataClassWithList([1])).to_json() ==
                '{"dc_with_list": {"xs": [1]}}')

    def test_nested_list_of_dataclasses(self):
        assert (DataClassXs([DataClassX(0), DataClassX(1)]).to_json() ==
                '{"xs": [{"x": 0}, {"x": 1}]}')


class TestDecoder:
    def test_nested_dataclass(self):
        assert (DataClassWithDataClass.from_json(
            '{"dc_with_list": {"xs": [1]}}') ==
                DataClassWithDataClass(DataClassWithList([1])))

    def test_nested_list_of_dataclasses(self):
        assert (DataClassXs.from_json('{"xs": [{"x": 0}, {"x": 1}]}') ==
                DataClassXs([DataClassX(0), DataClassX(1)]))
