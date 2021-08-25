from dataclasses import dataclass
from typing import TypeVar, Generic
from dataclasses_json import DataClassJsonMixin


T = TypeVar('T')
class ContainerCls(Generic[T]):
    value: T
    required: bool

@dataclass
class DataClassWithUnsupscriptedGeneric(DataClassJsonMixin):
    a: ContainerCls

@dataclass
class DataClassWithSupscriptedGeneric(DataClassJsonMixin):
    a: ContainerCls[int]

@dataclass
class DataClassWithParameterizedGeneric(DataClassJsonMixin, Generic[T]):
    a: ContainerCls[T]


class TestUnsupportedGenerics:
    def test_unsupscripted(self):
        j = '{ "a": { "value": "test", "required": true } }'
        dc = DataClassWithUnsupscriptedGeneric.from_json(j)
        assert dc.a == dict(value='test', required=True)
    
    def test_supscripted(self):
        j = '{ "a": { "value": 5, "required": false } }'
        dc = DataClassWithSupscriptedGeneric.from_json(j)
        assert dc.a == dict(value=5, required=False)
    
    def test_parameterized_unsupscripted(self):
        j = '{ "a": { "value": "test", "required": true } }'
        dc = DataClassWithParameterizedGeneric.from_json(j)
        assert dc.a == dict(value='test', required=True)
    
    def test_parameterized_supscripted(self):
        j = '{ "a": { "value": "test", "required": true } }'
        dc = DataClassWithParameterizedGeneric[str].from_json(j)
        assert dc.a == dict(value='test', required=True)
