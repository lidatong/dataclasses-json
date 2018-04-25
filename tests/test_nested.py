from tests.test_entities import (DataClassWithDataClass, DataClassWithList,
                                 DataClassX, DataClassXs)


class TestEncoder:
    def test_nested_dataclass(self):
        assert (DataClassWithDataClass(DataClassWithList([1])).to_json() ==
                '{"xs": {"xs": [1]}}')

    def test_nested_list_of_dataclasses(self):
        assert (DataClassXs([DataClassX(0), DataClassX(1)]).to_json() ==
                '{"xs": [{"x": 0}, {"x": 1}]}')


class TestDecoder:
    def test_nested_dataclass(self):
        print(DataClassWithDataClass.from_json('{"xs": {"xs": [1]}}'))
        print(DataClassWithDataClass(DataClassWithList([1])))
        assert (DataClassWithDataClass.from_json('{"xs": {"xs": [1]}}') ==
                DataClassWithDataClass(DataClassWithList([1])))

    def test_nested_list_of_dataclasses(self):
        assert (DataClassXs.from_json('{"xs": [{"x": 0}, {"x": 1}]}') ==
                DataClassXs([DataClassX(0), DataClassX(1)]))
