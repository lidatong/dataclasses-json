from dataclasses import dataclass
from typing import (Collection,
                    Deque,
                    FrozenSet,
                    List,
                    Optional,
                    Set,
                    Tuple,
                    TypeVar,
                    Union)

from dataclasses_json import DataClassJsonMixin

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
class DataClassWithUnionIntNone(DataClassJsonMixin):
    x: Union[int, None]


@dataclass(frozen=True)
class DataClassWithDataClass(DataClassJsonMixin):
    xs: DataClassWithList


@dataclass(frozen=True)
class DataClassX(DataClassJsonMixin):
    x: int


@dataclass(frozen=True)
class DataClassXs(DataClassJsonMixin):
    xs: List[DataClassX]


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
