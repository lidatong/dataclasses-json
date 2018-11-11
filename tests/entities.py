from dataclasses import dataclass, field
from typing import (Collection,
                    Deque,
                    Dict,
                    FrozenSet,
                    List,
                    Optional,
                    Set,
                    Tuple,
                    TypeVar,
                    Union)

from dataclasses_json import DataClassJsonMixin, dataclass_json
from uuid import UUID
from datetime import datetime

A = TypeVar('A')


@dataclass(frozen=True)
class DataClassWithList(DataClassJsonMixin):
    xs: List[int]


@dataclass(frozen=True)
class DataClassWithListDefaultFactory(DataClassJsonMixin):
    xs: List[int] = field(default_factory=list)


@dataclass(frozen=True)
class DataClassWithListStr(DataClassJsonMixin):
    xs: List[str]


@dataclass(frozen=True)
class DataClassWithDict(DataClassJsonMixin):
    kvs: Dict[str, str]


@dataclass(frozen=True)
class DataClassWithDictInt(DataClassJsonMixin):
    kvs: Dict[int, str]


@dataclass(frozen=True)
class DataClassWithDictDefaultFactory(DataClassJsonMixin):
    kvs: Dict[str, str] = field(default_factory=dict)


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
class DataClassWithOptionalNested(DataClassJsonMixin):
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
class DataClassMutableDefaultList(DataClassJsonMixin):
    xs: List[int] = field(default_factory=list)


@dataclass(frozen=True)
class DataClassMutableDefaultDict(DataClassJsonMixin):
    xs: Dict[str, int] = field(default_factory=dict)


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

@dataclass_json
@dataclass
class DataClassWithDatetime:
    created_at: datetime


@dataclass_json
@dataclass
class DataClassWithUuid:
    id: UUID

