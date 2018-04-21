from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from typing import List, Tuple, Set


@dataclass(frozen=True)
class DataClassWithList(DataClassJsonMixin):
    xs: List[int]


@dataclass(frozen=True)
class DataClassWithTuple(DataClassJsonMixin):
    xs: Tuple[int]


@dataclass(frozen=True)
class DataClassWithSet(DataClassJsonMixin):
    xs: Set[int]


@dataclass(frozen=True)
class DataclassWithDataclass(DataClassJsonMixin):
    xs: DataClassWithList


class TestEncoder:
    def test_list(self):
        assert DataClassWithList([1]).to_json() == '{"xs": [1]}'

    def test_set(self):
        assert DataClassWithSet({1}).to_json() == '{"xs": [1]}'

    def test_tuple(self):
        assert DataClassWithTuple((1,)).to_json() == '{"xs": [1]}'

    def test_nested_dataclass(self):
        assert (DataclassWithDataclass(DataClassWithList([1])).to_json() ==
                '{"xs": {"xs": [1]}}')


class TestDecoder:
    def test_list(self):
        assert (DataClassWithList.from_json('{"xs": [1]}') ==
                DataClassWithList([1]))

    def test_set(self):
        assert (DataClassWithSet.from_json('{"xs": [1]}') ==
                DataClassWithSet({1}))

    def test_tuple(self):
        assert (DataClassWithTuple.from_json('{"xs": [1]}') ==
                DataClassWithTuple((1,)))

    def test_nested_dataclass(self):
        assert (DataclassWithDataclass.from_json('{"xs": {"xs": [1]}}') ==
                DataclassWithDataclass(DataClassWithList([1])))
