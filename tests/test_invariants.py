from collections import deque

from hypothesis import given
from hypothesis.strategies import (frozensets, integers, lists, one_of, sets,
                                   tuples)

from tests.hypothesis2 import examples
from tests.hypothesis2.strategies import deques, optionals
from tests.test_entities import (DataClassWithDeque, DataClassWithFrozenSet,
                                 DataClassWithList, DataClassWithOptional,
                                 DataClassWithSet, DataClassWithTuple)

conss_to_strategies = [(DataClassWithList, lists, list),
                       (DataClassWithSet, sets, set),
                       (DataClassWithTuple, tuples, tuple),
                       (DataClassWithFrozenSet, frozensets,
                        frozenset),
                       (DataClassWithDeque, deques, deque),
                       (DataClassWithOptional, optionals,
                        lambda x: x)]
example_input = [1]


@given(one_of(*[strategy_fn(integers()).map(cons)
                for cons, strategy_fn, _ in conss_to_strategies]))
@examples(*[cons(f(example_input)) for cons, _, f in conss_to_strategies])
def test_generic_encode_and_decode_are_inverses(dc):
    assert dc.from_json(dc.to_json()) == dc
