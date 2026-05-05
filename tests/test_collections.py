from collections import Counter, deque

import pytest

from tests.entities import (DataClassIntImmutableDefault,
                            DataClassMutableDefaultDict,
                            DataClassMutableDefaultList, DataClassWithDeque,
                            DataClassWithDict, DataClassWithDictInt,
                            DataClassWithDictUnbound,
                            DataClassWithFrozenSet, DataClassWithList,
                            DataClassWithListUnbound, DataClassWithListStr, DataClassWithMyCollection,
                            DataClassWithOptional, DataClassWithOptionalStr,
                            DataClassWithSet, DataClassWithSetUnbound,
                            DataClassWithOptionalUnbound,
                            DataClassWithSetBuiltin,
                            DataClassWithDictBuiltin,
                            DataClassWithListBuiltin,
                            DataClassWithTupleBuiltin,
                            DataClassWithFrozenSetBuiltin,
                            DataClassWithDequeUnbound,
                            DataClassWithFrozenSetUnbound,
                            DataClassWithDequeCollections,
                            DataClassWithTuple, DataClassWithTupleUnbound,
                            DataClassWithUnionIntNone, MyCollection,
                            DataClassWithCounter, DataClassWithCollection,
                            DataClassWithMapping, DataClassWithMutableMapping,
                            DataClassWithMutableSet, DataClassWithMutableSequence,
                            DataClassWithSequence, DataClassWithAbstractSet)


class TestEncoder:
    def test_list(self):
        assert DataClassWithList([1]).to_json() == '{"xs": [1]}'

    def test_list_unbound(self):
        assert DataClassWithListUnbound([1]).to_json() == '{"xs": [1]}'

    def test_list_builtin(self):
        assert DataClassWithListBuiltin([1]).to_json() == '{"xs": [1]}'

    def test_list_str(self):
        assert DataClassWithListStr(['1']).to_json() == '{"xs": ["1"]}'

    def test_dict(self):
        assert DataClassWithDict({'1': 'a'}).to_json() == '{"kvs": {"1": "a"}}'

    def test_dict_unbound(self):
        assert DataClassWithDictUnbound({'1': 'a'}).to_json() == '{"kvs": {"1": "a"}}'

    def test_dict_builtin(self):
        assert DataClassWithDictBuiltin({'1': 'a'}).to_json() == '{"kvs": {"1": "a"}}'

    def test_dict_int(self):
        assert DataClassWithDictInt({1: 'a'}).to_json() == '{"kvs": {"1": "a"}}'

    def test_set(self):
        assert DataClassWithSet({1}).to_json() == '{"xs": [1]}'

    def test_set_unbound(self):
        assert DataClassWithSetUnbound({1}).to_json() == '{"xs": [1]}'

    def test_set_builtin(self):
        assert DataClassWithSetBuiltin({1}).to_json() == '{"xs": [1]}'

    def test_tuple(self):
        assert DataClassWithTuple((1,)).to_json() == '{"xs": [1]}'

    def test_tuple_unbound(self):
        assert DataClassWithTupleUnbound((1,)).to_json() == '{"xs": [1]}'

    def test_tuple_builtin(self):
        assert DataClassWithTupleBuiltin((1,)).to_json() == '{"xs": [1]}'

    def test_frozenset(self):
        assert DataClassWithFrozenSet(frozenset([1])).to_json() == '{"xs": [1]}'

    def test_frozenset_unbound(self):
        assert DataClassWithFrozenSetUnbound(frozenset([1])).to_json() == '{"xs": [1]}'

    def test_frozenset_builtin(self):
        assert DataClassWithFrozenSetBuiltin(frozenset([1])).to_json() == '{"xs": [1]}'

    def test_deque(self):
        assert DataClassWithDeque(deque([1])).to_json() == '{"xs": [1]}'

    def test_deque_unbound(self):
        assert DataClassWithDequeUnbound(deque([1])).to_json() == '{"xs": [1]}'

    def test_deque_builtin(self):
        assert DataClassWithDequeCollections(deque([1])).to_json() == '{"xs": [1]}'

    def test_optional(self):
        assert DataClassWithOptional(1).to_json() == '{"x": 1}'
        assert DataClassWithOptional(None).to_json() == '{"x": null}'

    def test_optional_unbound(self):
        assert DataClassWithOptionalUnbound(1).to_json() == '{"x": 1}'

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

    def test_counter(self):
        assert DataClassWithCounter(
            c=Counter('foo')).to_json() == '{"c": {"f": 1, "o": 2}}'


class TestDecoder:
    def test_list(self):
        assert (DataClassWithList.from_json('{"xs": [1]}') ==
                DataClassWithList([1]))

    def test_list_unbound(self):
        assert (DataClassWithListUnbound.from_json('{"xs": [1]}') ==
                DataClassWithListUnbound([1]))

    def test_list_builtin(self):
        assert (DataClassWithListBuiltin.from_json('{"xs": [1]}') ==
                DataClassWithListBuiltin([1]))

    def test_list_str(self):
        assert (DataClassWithListStr.from_json('{"xs": ["1"]}') ==
                DataClassWithListStr(["1"]))

    def test_dict(self):
        assert (DataClassWithDict.from_json('{"kvs": {"1": "a"}}') ==
                DataClassWithDict({'1': 'a'}))

    def test_dict_unbound(self):
        assert (DataClassWithDictUnbound.from_json('{"kvs": {"1": "a"}}') ==
                DataClassWithDictUnbound({'1': 'a'}))

    def test_dict_builtin(self):
        assert (DataClassWithDictBuiltin.from_json('{"kvs": {"1": "a"}}') ==
                DataClassWithDictBuiltin({'1': 'a'}))

    def test_dict_int(self):
        assert (DataClassWithDictInt.from_json('{"kvs": {"1": "a"}}') ==
                DataClassWithDictInt({1: 'a'}))

    def test_set(self):
        assert (DataClassWithSet.from_json('{"xs": [1]}') ==
                DataClassWithSet({1}))

    def test_set_unbound(self):
        assert (DataClassWithSetUnbound.from_json('{"xs": [1]}') ==
                DataClassWithSetUnbound({1}))

    def test_set_builtin(self):
        assert (DataClassWithSetBuiltin.from_json('{"xs": [1]}') ==
                DataClassWithSetBuiltin({1}))

    def test_tuple(self):
        assert (DataClassWithTuple.from_json('{"xs": [1]}') ==
                DataClassWithTuple((1,)))

    def test_tuple_unbound(self):
        assert (DataClassWithTupleUnbound.from_json('{"xs": [1]}') ==
                DataClassWithTupleUnbound((1,)))

    def test_tuple_builtin(self):
        assert (DataClassWithTupleBuiltin.from_json('{"xs": [1]}') ==
                DataClassWithTupleBuiltin((1,)))

    def test_frozenset(self):
        assert (DataClassWithFrozenSet.from_json('{"xs": [1]}') ==
                DataClassWithFrozenSet(frozenset([1])))

    def test_frozenset_unbound(self):
        assert (DataClassWithFrozenSetUnbound.from_json('{"xs": [1]}') ==
                DataClassWithFrozenSetUnbound(frozenset([1])))

    def test_frozenset_builtin(self):
        assert (DataClassWithFrozenSetBuiltin.from_json('{"xs": [1]}') ==
                DataClassWithFrozenSetBuiltin(frozenset([1])))

    def test_deque(self):
        assert (DataClassWithDeque.from_json('{"xs": [1]}') ==
                DataClassWithDeque(deque([1])))

    def test_deque_unbound(self):
        assert (DataClassWithDequeUnbound.from_json('{"xs": [1]}') ==
                DataClassWithDequeUnbound(deque([1])))

    def test_deque_collections(self):
        assert (DataClassWithDequeCollections.from_json('{"xs": [1]}') ==
                DataClassWithDequeCollections(deque([1])))

    def test_optional(self):
        assert (DataClassWithOptional.from_json('{"x": 1}') ==
                DataClassWithOptional(1))
        assert (DataClassWithOptional.from_json('{"x": null}') ==
                DataClassWithOptional(None))

    def test_optional_unbound(self):
        assert (DataClassWithOptionalUnbound.from_json('{"x": 1}') ==
                DataClassWithOptionalUnbound(1))
        assert (DataClassWithOptionalUnbound.from_json('{"x": null}') ==
                DataClassWithOptionalUnbound(None))

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

    def test_counter(self):
        assert DataClassWithCounter.from_json('{"c": {"f": 1, "o": 2}}') == \
               DataClassWithCounter(c=Counter('foo'))

    @pytest.mark.parametrize(
        "json_string, expected_instance",
        [
            pytest.param('{"c": [1, 2]}', DataClassWithCollection((1, 2)), id="collection"),
            pytest.param('{"c": [1, 2]}', DataClassWithSequence((1, 2)), id="sequence"),
            pytest.param('{"c": [1, 2]}', DataClassWithMutableSequence([1, 2]), id="mutable-sequence"),
            pytest.param('{"c": [1, 2]}', DataClassWithAbstractSet({1, 2}), id="set"),
            pytest.param('{"c": [1, 2]}', DataClassWithMutableSet({1, 2}), id="mutable-set"),
            pytest.param('{"c": {"1": 1, "2": 2}}', DataClassWithMapping({"1": 1, "2": 2}), id="mapping"),
            pytest.param('{"c": {"1": 1, "2": 2}}', DataClassWithMutableMapping({"1": 1, "2": 2}), id="mutable-mapping"),
       ]
    )
    def test_abstract_collections(self, json_string, expected_instance):
        assert type(expected_instance).from_json(json_string) == expected_instance
