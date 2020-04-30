from dataclasses import dataclass, field
from typing import Any, Dict, List

import pytest
import marshmallow

from dataclasses_json.core import Json
from dataclasses_json.api import dataclass_json, LetterCase, Undefined, \
    DataClassJsonMixin
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


@dataclass_json(undefined=Undefined.WARN)
@dataclass
class WarnApiDump:
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


class TestCatchAllUndefinedParameters:

    def test_it_dumps_undefined_parameters_back(self, invalid_response):
        dump = UnknownAPIDump.from_dict(invalid_response)
        inverse_dict = dump.to_dict()
        assert inverse_dict == invalid_response

    def test_dump_has_no_undefined_parameters_if_not_given(self,
                                                           valid_response):
        dump = UnknownAPIDump.from_dict(valid_response)
        assert dump.catch_all == {}

    def test_it_requires_a_catch_all_field(self, invalid_response):
        with pytest.raises(UndefinedParameterError):
            UnknownAPIDumpNoCatchAllField.from_dict(invalid_response)

    def test_it_requires_exactly_one_catch_all_field(self, invalid_response):
        @dataclass_json(undefined=Undefined.INCLUDE)
        @dataclass()
        class UnknownAPIDumpMultipleCatchAll:
            endpoint: str
            data: Dict[str, Any]
            catch_all: CatchAll
            catch_all2: CatchAll

        with pytest.raises(UndefinedParameterError):
            UnknownAPIDumpMultipleCatchAll.from_dict(invalid_response)

    def test_it_works_with_letter_case(self, invalid_response_camel_case):
        @dataclass_json(undefined=Undefined.INCLUDE,
                        letter_case=LetterCase.CAMEL)
        @dataclass()
        class UnknownAPIDumpCamelCase:
            endpoint: str
            data: Dict[str, Any]
            catch_all: CatchAll

        dump = UnknownAPIDumpCamelCase.from_dict(invalid_response_camel_case)
        assert {"undefinedFieldName": [1, 2, 3]} == dump.catch_all
        assert invalid_response_camel_case == dump.to_dict()

    def test_catch_all_field_name_cant_be_a_primitive_parameter(self,
                                                                valid_response):
        valid_response["catch_all"] = "some-value"
        with pytest.raises(UndefinedParameterError):
            UnknownAPIDump.from_dict(valid_response)

    def test_catch_all_field_can_be_initialized_with_dict(self,
                                                          invalid_response):
        invalid_response["catch_all"] = {"someValue": "some-stuff"}
        dump = UnknownAPIDump.from_dict(invalid_response)
        assert dump.catch_all == {"someValue": "some-stuff",
                                  "undefined_field_name": [1, 2, 3]}

    def test_it_raises_with_default_argument_and_catch_all_field_name(self,
                                                                      invalid_response):
        @dataclass_json(undefined="include")
        @dataclass()
        class UnknownAPIDumpDefault:
            endpoint: str
            data: Dict[str, Any]
            catch_all: CatchAll = None

        invalid_response["catch_all"] = "this should not happen"
        with pytest.raises(UndefinedParameterError):
            UnknownAPIDumpDefault.from_dict(invalid_response)

    def test_catch_all_field_can_have_default(self, valid_response,
                                              invalid_response):
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

    def test_catch_all_field_can_have_default_factory(self, valid_response,
                                                      invalid_response):
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

    def test_it_works_with_nested_schemata(self, boss_json):
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

    def test_it_dumps_nested_schemata_correctly(self, boss_json):
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
        assert "".join(boss_json.replace('\n', '').split()) == "".join(
            Boss.schema().dumps(boss).replace('\n', '').split())

    def test_it_preserves_nested_schemata_in_roundtrip(self, boss_json):
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

    def test_it_works_from_string(self, invalid_response):
        @dataclass_json(undefined="include")
        @dataclass()
        class UnknownAPIDumpFromString:
            endpoint: str
            data: Dict[str, Any]
            catch_all: CatchAll

        dump = UnknownAPIDumpFromString.from_dict(invalid_response)
        assert {"undefined_field_name": [1, 2, 3]} == dump.catch_all

    def test_it_works_with_valid_dict_expansion(self, valid_response):
        dump = UnknownAPIDump(**valid_response)
        assert dump.catch_all == {}

    def test_it_works_with_invalid_dict_expansion(self, invalid_response):
        dump = UnknownAPIDump(**invalid_response)
        assert {"undefined_field_name": [1, 2, 3]} == dump.catch_all

    def test_it_creates_dummy_keys_for_init_args(self):
        dump = UnknownAPIDump("some-endpoint", {"some-data": "foo"}, "unknown1",
                              "unknown2", undefined="123")
        assert dump.endpoint == "some-endpoint"
        assert dump.data == {"some-data": "foo"}
        assert dump.catch_all == {'_UNKNOWN0': 'unknown1',
                                  '_UNKNOWN1': 'unknown2',
                                  "undefined": "123"}

    def test_it_creates_dummy_keys_for_init_args_kwargs_mix(self):
        dump = UnknownAPIDump("some-endpoint", {"some-data": "foo"}, "unknown1",
                              "unknown2", catch_all={"bar": "example"},
                              undefined="123")
        assert dump.endpoint == "some-endpoint"
        assert dump.data == {"some-data": "foo"}
        assert dump.catch_all == {'_UNKNOWN0': 'unknown1',
                                  '_UNKNOWN1': 'unknown2',
                                  "bar": "example", "undefined": "123"}

    def test_it_doesnt_dump_the_default_value_without_undefined_parameters(
            self,
            valid_response):
        @dataclass_json(undefined="include")
        @dataclass()
        class UnknownAPIDumpDefault:
            endpoint: str
            data: Dict[str, Any]
            catch_all: CatchAll = None

        dump = UnknownAPIDumpDefault.from_dict(valid_response)
        assert dump.to_dict() == valid_response

    def test_it_dumps_default_factory_without_undefined_parameters(self,
                                                                   valid_response):
        @dataclass_json(undefined="include")
        @dataclass()
        class UnknownAPIDumpDefault:
            endpoint: str
            data: Dict[str, Any]
            catch_all: CatchAll = field(default_factory=dict)

        dump = UnknownAPIDumpDefault(**valid_response)
        assert dump.catch_all == {}


class TestRaiseUndefinedParameters:

    def test_it_raises_with_undefined_parameters(self, invalid_response):
        with pytest.raises(UndefinedParameterError):
            WellKnownAPIDump.from_dict(invalid_response)

    def test_it_doesnt_raise_with_known_parameters(self, valid_response):
        assert valid_response == WellKnownAPIDump.from_dict(
            valid_response).to_dict()

    def test_it_has_python_semantics_in_init(self, invalid_response):
        with pytest.raises(TypeError):
            WellKnownAPIDump(**invalid_response)


class TestIgnoreUndefinedParameters:

    def test_it_ignores_undefined_parameters(self, valid_response,
                                             invalid_response):
        from_valid = DontCareAPIDump.from_dict(valid_response)
        from_invalid = DontCareAPIDump.from_dict(invalid_response)
        assert from_valid == from_invalid

    def test_it_does_not_dump_undefined_parameters(self, invalid_response,
                                                   valid_response):
        dump = DontCareAPIDump.from_dict(invalid_response)
        dump_dict = dump.to_dict()
        assert valid_response == dump_dict

    def test_it_ignores_nested_schemata(self, boss_json):
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
        assert boss.minions == [Minion(name="evil minion"),
                                Minion(name="very evil minion")]

    def test_it_ignores_undefined_init_args(self):
        dump = DontCareAPIDump("some-endpoint", {"some-data": "foo"},
                               "unknown1",
                               "unknown2", undefined="123")
        assert dump.endpoint == "some-endpoint"
        assert dump.data == {"some-data": "foo"}

    def test_it_ignores_undefined_init_kwargs(self, invalid_response,
                                              valid_response):
        dump_invalid = DontCareAPIDump(**invalid_response)
        dump_valid = DontCareAPIDump(**valid_response)
        assert dump_valid == dump_invalid


class TestMiscellaneousUndefinedParameters:

    def test_it_raises_with_nested_schemata(self, boss_json):
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

    def test_it_works_with_catch_all_ignore_mix_nested_schemata(self,
                                                                boss_json):
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

    def test_it_only_acceps_valid_actions_as_string(self):
        with pytest.raises(UndefinedParameterError):
            @dataclass_json(undefined="not sure what this is supposed to do")
            @dataclass()
            class WontWork:
                endpoint: str
