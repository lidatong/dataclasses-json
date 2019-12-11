from dataclasses import dataclass
from typing import Any, Dict, List

import pytest
import marshmallow

from dataclasses_json.core import Json
from dataclasses_json.api import dataclass_json, LetterCase, UndefinedParameters
from dataclasses_json import CatchAll
from dataclasses_json.mm import UndefinedParameterError


@dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
@dataclass()
class UnknownAPIDump:
    endpoint: str
    data: Dict[str, Any]
    catch_all: CatchAll


@dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
@dataclass()
class UnknownAPIDumpNoCatchAllField:
    endpoint: str
    data: Dict[str, Any]


@dataclass_json(undefined_parameters=UndefinedParameters.RAISE)
@dataclass()
class WellKnownAPIDump:
    endpoint: str
    data: Dict[str, Any]


@dataclass_json(undefined_parameters=UndefinedParameters.EXCLUDE)
@dataclass
class DontCareAPIDump:
    endpoint: str
    data: Dict[str, Any]


@pytest.fixture
def valid_response() -> Dict[Any, Json]:
    return {"endpoint": "some_api_endpoint", "data": {"foo": 1, "bar": "2"}}


@pytest.fixture()
def invalid_response(valid_response):
    invalid_response = valid_response.copy()
    invalid_response["undefined_field_name"] = [1, 2, 3]
    return invalid_response


@pytest.fixture()
def invalid_response_camel_case(valid_response):
    invalid_response = valid_response.copy()
    invalid_response["undefinedFieldName"] = [1, 2, 3]
    return invalid_response


@pytest.fixture()
def boss_json():
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
    return boss_json


def test_undefined_parameters_catch_all_invalid_back(invalid_response):
    dump = UnknownAPIDump.from_dict(invalid_response)
    inverse_dict = dump.to_dict()
    assert invalid_response == inverse_dict


def test_undefined_parameters_catch_all_valid(valid_response):
    dump = UnknownAPIDump.from_dict(valid_response)
    assert dump.catch_all == {}


def test_undefined_parameters_catch_all_no_field(invalid_response):
    with pytest.raises(UndefinedParameterError):
        UnknownAPIDumpNoCatchAllField.from_dict(invalid_response)


def test_undefined_parameters_catch_all_multiple_fields(invalid_response):
    @dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
    @dataclass()
    class UnknownAPIDumpMultipleCatchAll:
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll
        catch_all2: CatchAll

    with pytest.raises(UndefinedParameterError):
        UnknownAPIDumpMultipleCatchAll.from_dict(invalid_response)


def test_undefined_parameters_catch_all_works_with_letter_case(invalid_response_camel_case):
    @dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE, letter_case=LetterCase.CAMEL)
    @dataclass()
    class UnknownAPIDumpCamelCase:
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll

    dump = UnknownAPIDumpCamelCase.from_dict(invalid_response_camel_case)
    assert {"undefinedFieldName": [1, 2, 3]} == dump.catch_all
    assert invalid_response_camel_case == dump.to_dict()


def test_undefined_parameters_catch_all_raises_if_initialized_with_catch_all_field_name(valid_response):
    valid_response["catch_all"] = "some-value"
    with pytest.raises(UndefinedParameterError):
        UnknownAPIDump.from_dict(valid_response)


def test_undefined_parameters_raise_invalid(invalid_response):
    with pytest.raises(UndefinedParameterError):
        WellKnownAPIDump.from_dict(invalid_response)


def test_undefined_parameters_raise_valid(valid_response):
    assert valid_response == WellKnownAPIDump.from_dict(valid_response).to_dict()


def test_undefined_parameters_ignore(valid_response, invalid_response):
    from_valid = DontCareAPIDump.from_dict(valid_response)
    from_invalid = DontCareAPIDump.from_dict(invalid_response)
    assert from_valid == from_invalid


def test_undefined_parameters_ignore_to_dict(invalid_response, valid_response):
    dump = DontCareAPIDump.from_dict(invalid_response)
    dump_dict = dump.to_dict()
    assert valid_response == dump_dict


def test_undefined_parameters_ignore_nested_schema(boss_json):
    @dataclass_json(undefined_parameters=UndefinedParameters.EXCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str

    @dataclass_json(undefined_parameters=UndefinedParameters.EXCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]

    boss = Boss.schema().loads(boss_json)
    assert len(boss.minions) == 2
    assert boss.minions == [Minion(name="evil minion"), Minion(name="very evil minion")]


def test_undefined_parameters_raise_nested_schema(boss_json):
    @dataclass_json(undefined_parameters=UndefinedParameters.RAISE)
    @dataclass(frozen=True)
    class Minion:
        name: str

    @dataclass_json(undefined_parameters=UndefinedParameters.EXCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]

    with pytest.raises(marshmallow.exceptions.ValidationError):
        Boss.schema().loads(boss_json)


def test_undefined_parameters_catch_all_nested_schema(boss_json):
    @dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str
        catch_all: CatchAll

    @dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]
        catch_all: CatchAll

    boss = Boss.schema().loads(boss_json)
    assert {"UNKNOWN_PROPERTY": "value"} == boss.catch_all
    assert {"UNKNOWN_PROPERTY": "value"} == boss.minions[0].catch_all
    assert {} == boss.minions[1].catch_all


def test_undefined_parameters_catch_all_schema_dump(boss_json):
    import json

    @dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str
        catch_all: CatchAll

    @dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]
        catch_all: CatchAll

    boss = Boss.schema().loads(boss_json)
    assert json.loads(boss_json) == Boss.schema().dump(boss)
    assert "".join(boss_json.replace('\n', '').split()) == "".join(Boss.schema().dumps(boss).replace('\n', '').split())


def test_undefined_parameters_catch_all_schema_roundtrip(boss_json):
    @dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str
        catch_all: CatchAll

    @dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]
        catch_all: CatchAll

    boss1 = Boss.schema().loads(boss_json)
    dumped_s = Boss.schema().dumps(boss1)
    boss2 = Boss.schema().loads(dumped_s)
    assert boss1 == boss2


def test_undefined_parameters_catch_all_ignore_mix_nested_schema(boss_json):
    @dataclass_json(undefined_parameters=UndefinedParameters.EXCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str

    @dataclass_json(undefined_parameters=UndefinedParameters.INCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]
        catch_all: CatchAll

    boss = Boss.schema().loads(boss_json)
    assert Minion(name="evil minion") == boss.minions[0]
    assert Minion(name="very evil minion") == boss.minions[1]
    assert {"UNKNOWN_PROPERTY": "value"} == boss.catch_all


def test_it_works_from_string(invalid_response):
    @dataclass_json(undefined_parameters="include")
    @dataclass()
    class UnknownAPIDumpFromString:
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll

    dump = UnknownAPIDumpFromString.from_dict(invalid_response)
    assert {"undefined_field_name": [1, 2, 3]} == dump.catch_all


def test_string_only_accepts_valid_actions():
    with pytest.raises(UndefinedParameterError):
        @dataclass_json(undefined_parameters="not sure what this is supposed to do")
        @dataclass()
        class WontWork:
            endpoint: str


def test_undefined_parameters_default_doesnt_do_anything(valid_response):
    @dataclass_json(undefined_parameters=UndefinedParameters.DEFAULT)
    @dataclass()
    class DefaultAPIDump:
        endpoint: str
        data: Dict[str, Any]

    dump = DefaultAPIDump.from_dict(valid_response)
    assert valid_response == dump.to_dict()