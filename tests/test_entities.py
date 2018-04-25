from typing import (List, Set, Tuple, FrozenSet, Deque, Optional, TypeVar,
                    Generic, Collection)

from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin
from collections import UserList

A = TypeVar('A')


@dataclass(frozen=True)
class DataClassWithList(DataClassJsonMixin):
    xs: List[int]


@dataclass(frozen=True)
class DataClassWithSet(DataClassJsonMixin):
    xs: Set[int]


@dataclass(frozen=True)
class DataClassWithTuple(DataClassJsonMixin):
    xs: Tuple[int]


@dataclass(frozen=True)
class DataClassWithFrozenSet(DataClassJsonMixin):
    xs: FrozenSet[int]


@dataclass(frozen=True)
class DataClassWithDeque(DataClassJsonMixin):
    xs: Deque[int]


@dataclass(frozen=True)
class DataClassWithOptional(DataClassJsonMixin):
    x: Optional[int]


@dataclass(frozen=True)
class DataClassWithDataClass(DataClassJsonMixin):
    xs: DataClassWithList


@dataclass(frozen=True)
class DataClassX(DataClassJsonMixin):
    x: int


@dataclass(frozen=True)
class DataClassXs(DataClassJsonMixin):
    xs: List[DataClassX]


class CustomList(Collection[A], UserList):
    pass


@dataclass(frozen=True)
class DataClassWithCustomList(DataClassJsonMixin):
    xs: CustomList[int]


class MyCollection(Collection[A]):
    def __init__(self, xs: Collection[A]):
        self.xs = xs

    def __contains__(self, item):
        return False

    def __iter__(self):
        return iter(self.xs)

    def __len__(self):
        return len(self.xs)

    def __eq__(self, other):
        return type(self) == type(other) and self.xs == other.xs


@dataclass(frozen=True)
class DataClassWithMyCollection(DataClassJsonMixin):
    xs: MyCollection[int]

