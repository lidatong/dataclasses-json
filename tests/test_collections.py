from collections import deque

from tests.entities import (DataClassIntImmutableDefault,
                            DataClassMutableDefaultDict,
                            DataClassMutableDefaultList, DataClassWithDeque,
                            DataClassWithDict, DataClassWithDictInt,
                            DataClassWithFrozenSet, DataClassWithList,
                            DataClassWithListStr, DataClassWithMyCollection,
                            DataClassWithOptional, DataClassWithOptionalStr,
                            DataClassWithSet, DataClassWithTuple,
                            DataClassWithUnionIntNone, MyCollection)


class TestEncoder:
    def test_list(self):
        assert DataClassWithList([1]).to_json() == '{"xs": [1]}'

    def test_list_str(self):
        assert DataClassWithListStr(['1']).to_json() == '{"xs": ["1"]}'

    def test_dict(self):
        assert DataClassWithDict({'1': 'a'}).to_json() == '{"kvs": {"1": "a"}}'

    def test_dict_int(self):
        assert DataClassWithDictInt({1: 'a'}).to_json() == '{"kvs": {"1": "a"}}'

    def test_set(self):
        assert DataClassWithSet({1}).to_json() == '{"xs": [1]}'

    def test_tuple(self):
        assert DataClassWithTuple((1,)).to_json() == '{"xs": [1]}'

    def test_frozenset(self):
        assert DataClassWithFrozenSet(frozenset([1])).to_json() == '{"xs": [1]}'

    def test_deque(self):
        assert DataClassWithDeque(deque([1])).to_json() == '{"xs": [1]}'

    def test_optional(self):
        assert DataClassWithOptional(1).to_json() == '{"x": 1}'
        assert DataClassWithOptional(None).to_json() == '{"x": null}'

    def test_optional_str(self):
        assert DataClassWithOptionalStr('1').to_json() == '{"x": "1"}'
        assert DataClassWithOptionalStr(None).to_json() == '{"x": null}'
        assert DataClassWithOptionalStr().to_json() == '{"x": null}'

    def test_union_int_none(self):
        assert DataClassWithUnionIntNone(1).to_json() == '{"x": 1}'
        assert DataClassWithUnionIntNone(None).to_json() == '{"x": null}'

    def test_my_collection(self):
        assert DataClassWithMyCollection(
            MyCollection([1])).to_json() == '{"xs": [1]}'

    def test_immutable_default(self):
        assert DataClassIntImmutableDefault().to_json() == '{"x": 0}'

    def test_mutable_default_list(self):
        assert DataClassMutableDefaultList().to_json() == '{"xs": []}'

    def test_mutable_default_dict(self):
        assert DataClassMutableDefaultDict().to_json() == '{"xs": {}}'


class TestDecoder:
    def test_list(self):
        assert (DataClassWithList.from_json('{"xs": [1]}') ==
                DataClassWithList([1]))

    def test_list_str(self):
        assert (DataClassWithListStr.from_json('{"xs": ["1"]}') ==
                DataClassWithListStr(["1"]))

    def test_dict(self):
        assert (DataClassWithDict.from_json('{"kvs": {"1": "a"}}') ==
                DataClassWithDict({'1': 'a'}))

    def test_dict_int(self):
        assert (DataClassWithDictInt.from_json('{"kvs": {"1": "a"}}') ==
                DataClassWithDictInt({1: 'a'}))

    def test_set(self):
        assert (DataClassWithSet.from_json('{"xs": [1]}') ==
                DataClassWithSet({1}))

    def test_tuple(self):
        assert (DataClassWithTuple.from_json('{"xs": [1]}') ==
                DataClassWithTuple((1,)))

    def test_frozenset(self):
        assert (DataClassWithFrozenSet.from_json('{"xs": [1]}') ==
                DataClassWithFrozenSet(frozenset([1])))

    def test_deque(self):
        assert (DataClassWithDeque.from_json('{"xs": [1]}') ==
                DataClassWithDeque(deque([1])))

    def test_optional(self):
        assert (DataClassWithOptional.from_json('{"x": 1}') ==
                DataClassWithOptional(1))
        assert (DataClassWithOptional.from_json('{"x": null}') ==
                DataClassWithOptional(None))

    def test_optional_str(self):
        assert (DataClassWithOptionalStr.from_json('{"x": "1"}') ==
                DataClassWithOptionalStr("1"))
        assert (DataClassWithOptionalStr.from_json('{"x": null}') ==
                DataClassWithOptionalStr(None))
        assert (DataClassWithOptionalStr.from_json('{}', infer_missing=True) ==
                DataClassWithOptionalStr())

    def test_my_collection(self):
        assert (DataClassWithMyCollection.from_json('{"xs": [1]}') ==
                DataClassWithMyCollection(MyCollection([1])))

    def test_immutable_default(self):
        assert (DataClassIntImmutableDefault.from_json('{"x": 0}')
                == DataClassIntImmutableDefault())
        assert (DataClassMutableDefaultList.from_json('{}', infer_missing=True)
                == DataClassMutableDefaultList())

    def test_mutable_default_list(self):
        assert (DataClassMutableDefaultList.from_json('{"xs": []}')
                == DataClassMutableDefaultList())
        assert (DataClassMutableDefaultList.from_json('{}', infer_missing=True)
                == DataClassMutableDefaultList())

    def test_mutable_default_dict(self):
        assert (DataClassMutableDefaultDict.from_json('{"kvs": {}}')
                == DataClassMutableDefaultDict())
        assert (DataClassMutableDefaultDict.from_json('{}', infer_missing=True)
                == DataClassMutableDefaultDict())
