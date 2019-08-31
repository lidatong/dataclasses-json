from collections import deque

from hypothesis import given
from hypothesis.strategies import (frozensets, integers, lists, one_of, sets,
                                   tuples)

from tests.entities import (DataClassWithDeque, DataClassWithFrozenSet,
                            DataClassWithList, DataClassWithOptional,
                            DataClassWithSet, DataClassWithTuple)
from tests.hypothesis2 import examples
from tests.hypothesis2.strategies import deques, optionals

dcconss_strategies_conss = [(DataClassWithList, lists, list),
                            (DataClassWithSet, sets, set),
                            (DataClassWithTuple, tuples, tuple),
                            (DataClassWithFrozenSet, frozensets, frozenset),
                            (DataClassWithDeque, deques, deque),
                            (DataClassWithOptional, optionals, lambda x: x)]
example_input = [1]


@given(one_of(*[strategy_fn(integers()).map(dccons)
                for dccons, strategy_fn, _ in dcconss_strategies_conss]))
@examples(*[dccons(cons(example_input))
            for dccons, _, cons in dcconss_strategies_conss])
def test_generic_encode_and_decode_are_inverses(dc):
    assert dc.from_json(dc.to_json()) == dc
