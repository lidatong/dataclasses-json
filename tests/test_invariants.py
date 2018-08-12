from collections import deque

from hypothesis import example, given
from hypothesis.strategies import (frozensets, integers, lists, one_of, sets,
                                   tuples)

from tests.strategies import deques, optionals
from tests.test_entities import (DataClassWithDeque,
                                 DataClassWithFrozenSet,
                                 DataClassWithList,
                                 DataClassWithSet,
                                 DataClassWithTuple,
                                 DataClassWithOptional)

conss_to_strategies = {DataClassWithList: lists,
                       DataClassWithSet: sets,
                       DataClassWithTuple: tuples,
                       DataClassWithFrozenSet: frozensets,
                       DataClassWithDeque: deques,
                       DataClassWithOptional: optionals}


@given(one_of(*[strategy_fn(integers()).map(cons)
                for cons, strategy_fn in conss_to_strategies.items()]))
@example(DataClassWithList([1]))
@example(DataClassWithSet({1}))
@example(DataClassWithTuple(tuple([1])))
@example(DataClassWithFrozenSet(frozenset([1])))
@example(DataClassWithDeque(deque([1])))
@example(DataClassWithOptional(1))
@example(DataClassWithOptional(None))
def test_generic_encode_and_decode_are_inverses(dc):
    assert dc.from_json(dc.to_json()) == dc
