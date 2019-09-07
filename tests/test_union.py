import pytest
from typing import *
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from marshmallow import ValidationError


# == Common use cases ==
@dataclass_json
@dataclass
class C1:
    f1: Union[int, str]


@dataclass_json
@dataclass
class C2:
    f1: Union[int, Dict[str, float]]


@dataclass_json
@dataclass
class C3:
    f1: Union[int, List[float]]


# == Use cases with nested dataclasses ==
@dataclass_json
@dataclass
class Aux1:
    f1: int


@dataclass_json
@dataclass
class Aux2:
    f1: str


@dataclass_json
@dataclass
class C4:
    f1: Union[Aux1, Aux2]


@dataclass_json
@dataclass
class C5:
    f1: Union[Aux1, Aux2, None]


@dataclass_json
@dataclass
class C6:
    f1: Union[Aux1, None]  # The same as Optional[Aux1]


@dataclass_json
@dataclass
class C7:
    f1: Union[C5, C6]


@dataclass_json
@dataclass
class C8:
    f1: Dict[str, Union[Aux1, Aux2]]


@dataclass_json
@dataclass
class C9:
    f1: List[Union[Aux1, Aux2]]


params = [
    (C1(f1=12), {"f1": 12}, '{"f1": 12}'),
    (C1(f1="str1"), {"f1": "str1"}, '{"f1": "str1"}'),

    (C2(f1=10), {"f1": 10}, '{"f1": 10}'),
    (C2(f1={"str1": 0.12}), {"f1": {"str1": 0.12}}, '{"f1": {"str1": 0.12}}'),

    (C3(f1=10), {"f1": 10}, '{"f1": 10}'),
    (C3(f1=[0.12, 0.13, 0.14]), {"f1": [0.12, 0.13, 0.14]}, '{"f1": [0.12, 0.13, 0.14]}'),

    (C4(f1=Aux1(1)), {"f1": {"f1": 1, "__type": "Aux1"}}, '{"f1": {"f1": 1, "__type": "Aux1"}}'),
    (C4(f1=Aux2("str1")), {"f1": {"f1": "str1", "__type": "Aux2"}}, '{"f1": {"f1": "str1", "__type": "Aux2"}}'),

    (C5(f1=Aux1(1)), {"f1": {"f1": 1, "__type": "Aux1"}}, '{"f1": {"f1": 1, "__type": "Aux1"}}'),
    (C5(f1=Aux2("str1")), {"f1": {"f1": "str1", "__type": "Aux2"}}, '{"f1": {"f1": "str1", "__type": "Aux2"}}'),
    (C5(f1=None), {"f1": None}, '{"f1": null}'),

    (C6(f1=Aux1(1)), {"f1": {"f1": 1}}, '{"f1": {"f1": 1}}'),  # For Optionals, type can be clearly defined
    (C6(f1=None), {"f1": None}, '{"f1": null}'),

    (C7(C5(Aux2("str1"))),
     {"f1": {"f1": {"f1": "str1", "__type": "Aux2"}, "__type": "C5"}},
     '{"f1": {"f1": {"f1": "str1", "__type": "Aux2"}, "__type": "C5"}}'),
    (C7(C6(Aux1(12))),
     {"f1": {"f1": {"f1": 12}, "__type": "C6"}},
     '{"f1": {"f1": {"f1": 12}, "__type": "C6"}}'),

    (C8({"str1": Aux1(12), "str2": Aux2("str3")}),
     {"f1": {"str1": {"f1": 12, "__type": "Aux1"}, "str2": {"f1": "str3", "__type": "Aux2"}}},
     '{"f1": {"str1": {"f1": 12, "__type": "Aux1"}, "str2": {"f1": "str3", "__type": "Aux2"}}}'),

    (C9([Aux1(12), Aux2("str3")]),
     {"f1": [{"f1": 12, "__type": "Aux1"}, {"f1": "str3", "__type": "Aux2"}]},
     '{"f1": [{"f1": 12, "__type": "Aux1"}, {"f1": "str3", "__type": "Aux2"}]}')
]


@pytest.mark.parametrize('obj, expected, expected_json', params)
def test_serialize(obj, expected, expected_json):
    s = obj.schema()
    assert s.dump(obj) == expected
    assert s.dumps(obj) == expected_json


@pytest.mark.parametrize('expected_obj, data, data_json', params)
def test_deserialize(expected_obj, data, data_json):
    cls = type(expected_obj)
    s = cls.schema()
    assert s.load(data) == expected_obj
    assert s.loads(data_json) == expected_obj


def test_deserialize_twice():
    data = {"f1": [{"f1": 12, "__type": "Aux1"}, {"f1": "str3", "__type": "Aux2"}]}
    expected_obj = C9([Aux1(12), Aux2("str3")])

    s = C9.schema()
    res1 = s.load(data)
    res2 = s.load(data)
    assert res1 == expected_obj and res2 == expected_obj


@pytest.mark.parametrize('obj', [
    (C2(f1={"str1": "str1"})),
    (C3(f1=[0.12, 0.13, "str1"])),
])
def test_serialize_with_error(obj):
    s = obj.schema()
    with pytest.raises(ValueError):
        assert s.dump(obj)


@pytest.mark.parametrize('cls, data', [
    (C1, {"f1": None}),
])
def test_deserialize_with_error(cls, data):
    s = cls.schema()
    with pytest.raises(ValidationError):
        assert s.load(data)
