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
