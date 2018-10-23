from dataclasses import dataclass, field
from typing import (Collection,
                    Deque,
                    FrozenSet,
                    List,
                    Optional,
                    Set,
                    Tuple,
                    TypeVar,
                    Union)

from dataclasses_json import DataClassJsonMixin, dataclass_json

A = TypeVar('A')


@dataclass(frozen=True)
class DataClassWithList(DataClassJsonMixin):
    xs: List[int]


@dataclass(frozen=True)
class DataClassWithListStr(DataClassJsonMixin):
    xs: List[str]


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


@dataclass
class DataClassWithOptionalStr(DataClassJsonMixin):
    x: Optional[str] = None


@dataclass(frozen=True)
class DataClassWithOptionalRecursive(DataClassJsonMixin):
    x: Optional[DataClassWithOptional]


@dataclass(frozen=True)
class DataClassWithUnionIntNone(DataClassJsonMixin):
    x: Union[int, None]


@dataclass(frozen=True)
class DataClassWithDataClass(DataClassJsonMixin):
    dc_with_list: DataClassWithList


@dataclass(frozen=True)
class DataClassX(DataClassJsonMixin):
    x: int


@dataclass(frozen=True)
class DataClassXs(DataClassJsonMixin):
    xs: List[DataClassX]


@dataclass(frozen=True)
class DataClassImmutableDefault(DataClassJsonMixin):
    x: int = 0


@dataclass(frozen=True)
class DataClassMutableDefault(DataClassJsonMixin):
    xs: List[int] = field(default_factory=list)


class MyCollection(Collection[A]):
    def __init__(self, xs: Collection[A]) -> None:
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


@dataclass_json
@dataclass
class DataClassJsonDecorator:
    x: str
