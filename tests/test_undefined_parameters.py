from dataclasses import dataclass
from typing import Any, Dict, List

import pytest
import marshmallow

from dataclasses_json.core import Json, UndefinedParameterError, UndefinedParameters
from dataclasses_json.mm import CatchAll
from dataclasses_json.api import dataclass_json


@dataclass_json(undefined_parameters=UndefinedParameters.CATCH_ALL)
@dataclass()
class UnknownAPIDump:
    endpoint: str
    data: Dict[str, Any]
    catch_all: CatchAll


@dataclass_json(undefined_parameters=UndefinedParameters.CATCH_ALL)
@dataclass()
class UnknownAPIDumpNoCatchAllField:
    endpoint: str
    data: Dict[str, Any]


@dataclass_json(undefined_parameters=UndefinedParameters.RAISE)
@dataclass()
class WellKnownAPIDump:
    endpoint: str
    data: Dict[str, Any]


@dataclass_json(undefined_parameters=UndefinedParameters.IGNORE)
@dataclass
class DontCareAPIDump:
    endpoint: str
    data: Dict[str, Any]


@pytest.fixture
def valid_response() -> Dict[Any, Json]:
    return {"endpoint": "some_api_endpoint", "data": {"foo": 1, "bar": "2"}}


@pytest.fixture()
def invalid_response(valid_response):
    valid_response["undefined_field_name"] = [1, 2, 3]
    return valid_response


def test_undefined_parameters_catch_all_invalid(invalid_response):
    dump = UnknownAPIDump.from_dict(invalid_response)
    assert dump.catch_all == {"undefined_field_name": invalid_response["undefined_field_name"]}


def test_undefined_parameters_catch_all_valid(valid_response):
    dump = UnknownAPIDump.from_dict(valid_response)
    assert dump.catch_all == {}


def test_undefined_parameters_catch_all_no_field(invalid_response):
    with pytest.raises(UndefinedParameterError):
        UnknownAPIDumpNoCatchAllField.from_dict(invalid_response)


def test_undefined_parameters_raise_invalid(invalid_response):
    with pytest.raises(UndefinedParameterError):
        WellKnownAPIDump.from_dict(invalid_response)


def test_undefined_parameters_raise_valid(valid_response):
    assert valid_response == WellKnownAPIDump.from_dict(valid_response).to_dict()


def test_undefined_parameters_ignore(valid_response, invalid_response):
    from_valid = DontCareAPIDump.from_dict(valid_response)
    from_invalid = DontCareAPIDump.from_dict(invalid_response)
    assert from_valid == from_invalid


def test_undefined_parameters_ignore_nested():
    @dataclass_json(undefined_parameters=UndefinedParameters.IGNORE)
    @dataclass(frozen=True)
    class Minion:
        name: str

    @dataclass_json
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]

    boss_json = """
    {
        "minions": [
            {
                "name": "evil minion", 
                "UNKNOWN_PROPERTY" : "value"
            },
            {
                "name": "very evil minion"
            }
        ],
        "UNKNOWN_PROPERTY" : "value"
    }
    """.strip()
    boss = Boss.schema(unknown=marshmallow.INCLUDE).loads(boss_json)
    assert len(boss.minions) == 2
    assert boss.minions == [Minion(name="evil minion"), Minion(name="very evil minion")]
