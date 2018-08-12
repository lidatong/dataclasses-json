from hypothesis.strategies import lists, one_of, none
from collections import deque


def deques(elements=None, min_size=None, average_size=None, max_size=None,
           unique_by=None, unique=False):
    return lists(**locals()).map(deque)


def optionals(strategy):
    return one_of(strategy, none())
