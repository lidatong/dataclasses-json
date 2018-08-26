from collections import deque

from tests.entities import (DataClassWithDeque,
                            DataClassWithFrozenSet,
                            DataClassWithList,
                            DataClassWithMyCollection,
                            DataClassWithOptional,
                            DataClassWithOptionalRecursive,
                            DataClassWithSet,
                            DataClassWithTuple,
                            DataClassWithUnionIntNone,
                            MyCollection,
                            DataClassImmutableDefault,
                            DataClassMutableDefault)


class TestEncoder:
    def test_list(self):
        assert DataClassWithList([1]).to_json() == '{"xs": [1]}'

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

    def test_union_int_none(self):
        assert DataClassWithUnionIntNone(1).to_json() == '{"x": 1}'
        assert DataClassWithUnionIntNone(None).to_json() == '{"x": null}'

    def test_my_collection(self):
        assert DataClassWithMyCollection(
            MyCollection([1])).to_json() == '{"xs": [1]}'

    def test_immutable_default(self):
        assert DataClassImmutableDefault().to_json() == '{"x": 0}'

    def test_mutable_default(self):
        assert DataClassMutableDefault().to_json() == '{"xs": []}'


class TestDecoder:
    def test_list(self):
        assert (DataClassWithList.from_json('{"xs": [1]}') ==
                DataClassWithList([1]))

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

    def test_infer_missing(self):
        actual = DataClassWithOptional.from_json('{}', infer_missing=True)
        assert (actual == DataClassWithOptional(None))

    def test_infer_missing_is_recursive(self):
        actual = DataClassWithOptionalRecursive.from_json('{"x": null}',
                                                          infer_missing=True)
        assert (actual == DataClassWithOptionalRecursive(
            DataClassWithOptional(None)))

    def test_my_collection(self):
        assert (DataClassWithMyCollection.from_json('{"xs": [1]}') ==
                DataClassWithMyCollection(MyCollection([1])))

    def test_my_list_collection(self):
        assert (DataClassWithMyCollection.from_json_array('[{"xs": [1]}]')
                == [DataClassWithMyCollection(MyCollection([1]))])

    def test_immutable_default(self):
        assert (DataClassImmutableDefault.from_json('{"x": 0}')
                == DataClassImmutableDefault())

    def test_mutable_default(self):
        assert (DataClassMutableDefault.from_json('{"xs": []}')
                == DataClassMutableDefault())
