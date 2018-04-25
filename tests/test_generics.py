from collections import deque

from tests.test_entities import (DataClassWithList, DataClassWithSet,
                                 DataClassWithTuple, DataClassWithFrozenSet,
                                 DataClassWithDeque, DataClassWithOptional,
                                 DataClassWithCustomList, CustomList,
                                 DataClassWithMyCollection,
                                 MyCollection)


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

    def test_custom_list(self):
        assert (DataClassWithCustomList(CustomList([1])).to_json() ==
                '{"xs": [1]}')

    def test_my_collection(self):
        assert DataClassWithMyCollection(MyCollection([1])).to_json() == '{"xs": [1]}'


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

    def test_custom_list(self):
        print(DataClassWithCustomList.from_json('{"xs": [1]}'))
        assert (DataClassWithCustomList.from_json('{"xs": [1]}') ==
                DataClassWithCustomList(CustomList([1])))

    def test_my_collection(self):
        assert (DataClassWithMyCollection.from_json('{"xs": [1]}') ==
                DataClassWithMyCollection(MyCollection([1])))
