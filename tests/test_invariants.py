from hypothesis import given
from hypothesis.strategies import (text, lists, integers, sets, frozensets,
                                   tuples, one_of)
from tests.strategies import deques, optionals

from tests.test_entities import (DataClassWithDeque,
                                 DataClassWithFrozenSet,
                                 DataClassWithList,
                                 DataClassWithMyCollection,
                                 DataClassWithOptional,
                                 DataClassWithSet,
                                 DataClassWithTuple,
                                 DataClassWithUnionIntNone,
                                 MyCollection)
import pytest


@given(one_of(*[strategy(integers()).map(cons) for cons, strategy in
                {DataClassWithList: lists,
                 DataClassWithSet: sets,
                 DataClassWithTuple: tuples,
                 DataClassWithFrozenSet: frozensets,
                 DataClassWithDeque: deques}.items()]))
def test_collection_encode_and_decode_are_inverses(dc):
    print(dc)
    assert dc.from_json(dc.to_json()) == dc

# def make_test_collection_encode_and_decode_are_inverses(dc_collection):
#     def test_encode_and_decode_are_inverses(xs):
#
#     return test_encode_and_decode_are_inverses


# @given(lists(integers()))
# def test_list_encode_and_decode_are_inverses(xs):
#     make_test_collection_encode_and_decode_are_inverses(DataClassWithList)(xs)
#
#
# @given(sets(integers()))
# def test_set_encode_and_decode_are_inverses(xs):
#     make_test_collection_encode_and_decode_are_inverses(DataClassWithSet)(xs)
#
#
# @given(lists(integers()))
# def test_tuple_encode_and_decode_are_inverses(xs):
#     make_test_collection_encode_and_decode_are_inverses(DataClassWithTuple)(xs)
#
#
# @given(frozensets(integers()))
# def test_frozenset_encode_and_decode_are_inverses(xs):
#     make_test_collection_encode_and_decode_are_inverses(
#         DataClassWithFrozenSet)(xs)
#
#
# @given(deques(integers()))
# def test_deque_encode_and_decode_are_inverses(xs):
#     make_test_collection_encode_and_decode_are_inverses(DataClassWithDeque)(xs)


# @given(optionals(integers()))
# def test_optional_encode_and_decode_are_inverses(xs):
#     make_test_collection_encode_and_decode_are_inverses(DataClassWithDeque)(xs)
