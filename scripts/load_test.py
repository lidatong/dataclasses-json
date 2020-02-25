from builtins import list
from random import randint
from typing import List, Dict, Any

from dataclasses_json import dataclass_json, DataClassJsonMixin
from time import time
from dataclasses import dataclass, field


@dataclass_json
@dataclass(frozen=True)
class AnotherNestedDataclass(DataClassJsonMixin):
    more_stuff: List[int] = field(default_factory=list)
    x: str = "a"
    y: str = "b"
    z: str = "c"
    dict_key: Dict[str, Any] = field(default_factory=dict)
    key: Any = "some_super_value"


@dataclass_json
@dataclass(frozen=True)
class NestedDataclass(DataClassJsonMixin):
    super_complicated: AnotherNestedDataclass = AnotherNestedDataclass()
    stuff: List[AnotherNestedDataclass] = field(default_factory=list)
    a: float = 0.0
    b: float = 0.0
    c: float = 0.0


@dataclass_json
@dataclass(frozen=True)
class BigDataclass(DataClassJsonMixin):
    nested: List[NestedDataclass] = field(default_factory=list)
    top_level_dict: Dict[str, Any] = field(default_factory=dict)


if __name__ == '__main__':
    to_parse: List[BigDataclass] = list()
    for i in range(1, 100):
        ints = [randint(1, 100)]*50
        nested_dataclass = NestedDataclass(stuff=[AnotherNestedDataclass(more_stuff=ints)]*50)
        to_parse.append(BigDataclass(nested=[nested_dataclass]*50))

    start = time()
    json = list(map(lambda dc: dc.to_dict(), to_parse))
    end = time()
    print(f"It took {end-start}s to convert to dict")

    start = time()

    list = list(map(BigDataclass.from_dict, json))

    end = time()

    print(f"It took {end-start}s to convert from dict")