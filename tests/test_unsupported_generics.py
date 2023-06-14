from dataclasses import dataclass
from typing import TypeVar, Generic

from dataclasses_json import DataClassJsonMixin


T = TypeVar('T')
class ContainerCls(Generic[T]):
    value: T
    required: bool

@dataclass
class DataClassWithUnsubscriptedGeneric(DataClassJsonMixin):
    a: ContainerCls

@dataclass
class DataClassWithSubscriptedGeneric(DataClassJsonMixin):
    a: ContainerCls[int]

@dataclass
class DataClassWithParameterizedGeneric(DataClassJsonMixin, Generic[T]):
    a: ContainerCls[T]


class TestUnsupportedGenerics:
    def test_unsubscripted(self):
        j = '{ "a": { "value": "test", "required": true } }'
        dc = DataClassWithUnsubscriptedGeneric.from_json(j)
        assert dc.a == dict(value='test', required=True)
    
    def test_subscripted(self):
        j = '{ "a": { "value": 5, "required": false } }'
        dc = DataClassWithSubscriptedGeneric.from_json(j)
        assert dc.a == dict(value=5, required=False)
    
    def test_parameterized_unsubscripted(self):
        j = '{ "a": { "value": "test", "required": true } }'
        dc = DataClassWithParameterizedGeneric.from_json(j)
        assert dc.a == dict(value='test', required=True)
    
    def test_parameterized_subscripted(self):
        j = '{ "a": { "value": "test", "required": true } }'
        dc = DataClassWithParameterizedGeneric[str].from_json(j)
        assert dc.a == dict(value='test', required=True)
