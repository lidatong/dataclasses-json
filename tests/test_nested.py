from tests.entities import (DataClassMappingBadDecode,
                            DataClassWithDataClass,
                            DataClassWithList,
                            DataClassWithNestedDictWithTupleKeys,
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

    def test_nested_mapping_of_dataclasses(self):
        err = None
        try:
            DataClassMappingBadDecode.from_dict(dict(map=dict(test=dict(id="irrelevant"))))
        except TypeError as e:
            if "positional arguments" not in e.args[0]:
                raise
            err = e
        assert isinstance(err, TypeError)


class TestNested:
    def test_tuple_dict_key(self):
        assert (DataClassWithNestedDictWithTupleKeys.from_dict({'a': {(0,): 2}}) ==
                DataClassWithNestedDictWithTupleKeys(a={(0,): 2}))

