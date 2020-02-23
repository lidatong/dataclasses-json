from dataclasses import dataclass, field
from typing import Any, Dict, List

import pytest
import marshmallow

from dataclasses_json.core import Json
from dataclasses_json.api import dataclass_json, LetterCase, Undefined, DataClassJsonMixin
from dataclasses_json import CatchAll
from dataclasses_json.undefined import UndefinedParameterError


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass()
class UnknownAPIDump:
    endpoint: str
    data: Dict[str, Any]
    catch_all: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass()
class UnknownAPIDumpNoCatchAllField:
    endpoint: str
    data: Dict[str, Any]


@dataclass_json(undefined=Undefined.RAISE)
@dataclass()
class WellKnownAPIDump:
    endpoint: str
    data: Dict[str, Any]


@dataclass_json(undefined=Undefined.EXCLUDE)
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
    assert inverse_dict == invalid_response


def test_undefined_parameters_catch_all_valid(valid_response):
    dump = UnknownAPIDump.from_dict(valid_response)
    assert dump.catch_all == {}


def test_undefined_parameters_catch_all_no_field(invalid_response):
    with pytest.raises(UndefinedParameterError):
        UnknownAPIDumpNoCatchAllField.from_dict(invalid_response)


def test_undefined_parameters_catch_all_multiple_fields(invalid_response):
    @dataclass_json(undefined=Undefined.INCLUDE)
    @dataclass()
    class UnknownAPIDumpMultipleCatchAll:
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll
        catch_all2: CatchAll

    with pytest.raises(UndefinedParameterError):
        UnknownAPIDumpMultipleCatchAll.from_dict(invalid_response)


def test_undefined_parameters_catch_all_works_with_letter_case(invalid_response_camel_case):
    @dataclass_json(undefined=Undefined.INCLUDE, letter_case=LetterCase.CAMEL)
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


def test_undefined_parameters_catch_all_initialized_with_dict_and_more_unknown(invalid_response):
    invalid_response["catch_all"] = {"someValue": "some-stuff"}
    dump = UnknownAPIDump.from_dict(invalid_response)
    assert dump.catch_all == {"someValue": "some-stuff", "undefined_field_name": [1, 2, 3]}


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
    @dataclass_json(undefined=Undefined.EXCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str

    @dataclass_json(undefined=Undefined.EXCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]

    boss = Boss.schema().loads(boss_json)
    assert len(boss.minions) == 2
    assert boss.minions == [Minion(name="evil minion"), Minion(name="very evil minion")]


def test_undefined_parameters_raise_nested_schema(boss_json):
    @dataclass_json(undefined=Undefined.RAISE)
    @dataclass(frozen=True)
    class Minion:
        name: str

    @dataclass_json(undefined=Undefined.EXCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]

    with pytest.raises(marshmallow.exceptions.ValidationError):
        Boss.schema().loads(boss_json)


def test_undefined_parameters_catch_all_nested_schema(boss_json):
    @dataclass_json(undefined=Undefined.INCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str
        catch_all: CatchAll

    @dataclass_json(undefined=Undefined.INCLUDE)
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

    @dataclass_json(undefined=Undefined.INCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str
        catch_all: CatchAll

    @dataclass_json(undefined=Undefined.INCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]
        catch_all: CatchAll

    boss = Boss.schema().loads(boss_json)
    assert json.loads(boss_json) == Boss.schema().dump(boss)
    assert "".join(boss_json.replace('\n', '').split()) == "".join(Boss.schema().dumps(boss).replace('\n', '').split())


def test_undefined_parameters_catch_all_schema_roundtrip(boss_json):
    @dataclass_json(undefined=Undefined.INCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str
        catch_all: CatchAll

    @dataclass_json(undefined=Undefined.INCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]
        catch_all: CatchAll

    boss1 = Boss.schema().loads(boss_json)
    dumped_s = Boss.schema().dumps(boss1)
    boss2 = Boss.schema().loads(dumped_s)
    assert boss1 == boss2


def test_undefined_parameters_catch_all_ignore_mix_nested_schema(boss_json):
    @dataclass_json(undefined=Undefined.EXCLUDE)
    @dataclass(frozen=True)
    class Minion:
        name: str

    @dataclass_json(undefined=Undefined.INCLUDE)
    @dataclass(frozen=True)
    class Boss:
        minions: List[Minion]
        catch_all: CatchAll

    boss = Boss.schema().loads(boss_json)
    assert Minion(name="evil minion") == boss.minions[0]
    assert Minion(name="very evil minion") == boss.minions[1]
    assert {"UNKNOWN_PROPERTY": "value"} == boss.catch_all


def test_it_works_from_string(invalid_response):
    @dataclass_json(undefined="include")
    @dataclass()
    class UnknownAPIDumpFromString:
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll

    dump = UnknownAPIDumpFromString.from_dict(invalid_response)
    assert {"undefined_field_name": [1, 2, 3]} == dump.catch_all


def test_string_only_accepts_valid_actions():
    with pytest.raises(UndefinedParameterError):
        @dataclass_json(undefined="not sure what this is supposed to do")
        @dataclass()
        class WontWork:
            endpoint: str


def test_undefined_parameters_raises_with_default_argument_and_supplied_catch_all_name(invalid_response):
    @dataclass_json(undefined="include")
    @dataclass()
    class UnknownAPIDumpDefault:
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll = None

    invalid_response["catch_all"] = "this should not happen"
    with pytest.raises(UndefinedParameterError):
        UnknownAPIDumpDefault.from_dict(invalid_response)


def test_undefined_parameters_doesnt_raise_with_default(valid_response, invalid_response):
    @dataclass_json(undefined="include")
    @dataclass()
    class UnknownAPIDumpDefault:
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll = None

    from_valid = UnknownAPIDumpDefault.from_dict(valid_response)
    from_invalid = UnknownAPIDumpDefault.from_dict(invalid_response)
    assert from_valid.catch_all is None
    assert {"undefined_field_name": [1, 2, 3]} == from_invalid.catch_all


def test_undefined_parameters_doesnt_raise_with_default_factory(valid_response, invalid_response):
    @dataclass_json(undefined="include")
    @dataclass()
    class UnknownAPIDumpDefault(DataClassJsonMixin):
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll = field(default_factory=dict)

    from_valid = UnknownAPIDumpDefault.from_dict(valid_response)
    from_invalid = UnknownAPIDumpDefault.from_dict(invalid_response)
    assert from_valid.catch_all == {}
    assert {"undefined_field_name": [1, 2, 3]} == from_invalid.catch_all


def test_undefined_parameters_catch_all_init_valid(valid_response):
    dump = UnknownAPIDump(**valid_response)
    assert dump.catch_all == {}


def test_undefined_parameters_catch_all_init_invalid(invalid_response):
    dump = UnknownAPIDump(**invalid_response)
    assert {"undefined_field_name": [1, 2, 3]} == dump.catch_all


def test_undefined_parameters_catch_all_init_args():
    dump = UnknownAPIDump("some-endpoint", {"some-data": "foo"}, "unknown1", "unknown2", undefined="123")
    assert dump.endpoint == "some-endpoint"
    assert dump.data == {"some-data": "foo"}
    assert dump.catch_all == {'_UNKNOWN0': 'unknown1', '_UNKNOWN1': 'unknown2', "undefined": "123"}


def test_undefined_parameters_catch_all_init_args_kwargs_mixed():
    dump = UnknownAPIDump("some-endpoint", {"some-data": "foo"}, "unknown1", "unknown2", catch_all={"bar": "example"},
                          undefined="123")
    assert dump.endpoint == "some-endpoint"
    assert dump.data == {"some-data": "foo"}
    assert dump.catch_all == {'_UNKNOWN0': 'unknown1', '_UNKNOWN1': 'unknown2', "bar": "example", "undefined": "123"}


def test_undefined_parameters_ignore_init_args():
    dump = DontCareAPIDump("some-endpoint", {"some-data": "foo"}, "unknown1", "unknown2", undefined="123")
    assert dump.endpoint == "some-endpoint"
    assert dump.data == {"some-data": "foo"}


def test_undefined_parameters_ignore_init_invalid(invalid_response, valid_response):
    dump_invalid = DontCareAPIDump(**invalid_response)
    dump_valid = DontCareAPIDump(**valid_response)
    assert dump_valid == dump_invalid


def test_undefined_parameters_raise_init(invalid_response):
    with pytest.raises(TypeError):
        WellKnownAPIDump(**invalid_response)


def test_undefined_parameters_catch_all_default_no_undefined(valid_response):
    @dataclass_json(undefined="include")
    @dataclass()
    class UnknownAPIDumpDefault:
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll = None

    dump = UnknownAPIDumpDefault.from_dict(valid_response)
    assert dump.to_dict() == valid_response


def test_undefined_parameters_catch_all_default_factory_init_converts_factory(valid_response):
    @dataclass_json(undefined="include")
    @dataclass()
    class UnknownAPIDumpDefault:
        endpoint: str
        data: Dict[str, Any]
        catch_all: CatchAll = field(default_factory=dict)

    dump = UnknownAPIDumpDefault(**valid_response)
    assert dump.catch_all == {}