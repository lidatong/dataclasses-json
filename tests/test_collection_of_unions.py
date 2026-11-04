from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, Union, List, Optional
import json
import warnings

import pytest

from dataclasses_json import CatchAll, Undefined, config, dataclass_json
from dataclasses_json.undefined import UndefinedParameterError


@dataclass_json
@dataclass(frozen=True)
class TestChild:
    some_field: int = None


@dataclass_json
@dataclass(frozen=True)
class TestOtherChild:
    other_field: int = None


@dataclass_json
@dataclass(frozen=True)
class DictUnion:
    d: Dict[str, Union[TestChild, TestOtherChild]]


@dataclass_json
@dataclass(frozen=True)
class ListUnion:
    l: List[Union[TestChild, TestOtherChild]]


@dataclass_json
@dataclass(frozen=True)
class Player:
    name: str


@dataclass_json
@dataclass(frozen=True)
class Team:
    roster: List[Union[int, Player]]
    roster_backup: Dict[int, Union[int, Player]]


class TestCollectionOfUnions:
    def test_dict(self):
        data = {
            'd': {
                'child' : {
                    'some_field' : 1
                },
                'other_child' : {
                    'other_field' : 2
                }
            }
        }
        json_str = json.dumps(data)
        obj = DictUnion.from_json(json_str)

        assert type(obj.d['child']) in (TestChild, TestOtherChild)

    def test_list(self):
        data = {
            'l': [
                {
                    'some_field' : 1
                },
                {
                    'other_field' : 1
                }
            ]
        }
        json_str = json.dumps(data)
        obj = ListUnion.from_json(json_str)

        assert type(obj.l[0]) in (TestChild, TestOtherChild)

    def test_int(self):
        data = {
            'roster': [
                1,
                2,
                3
            ],
            'roster_backup': {
                1: 5,
                2: 3,
                3: 2
            }
        }
        json_str = json.dumps(data)
        obj: Team = Team.from_json(json_str)

        assert type(obj.roster[0]) is int and type(obj.roster_backup[1]) is int

    def test_dataclass(self):
        data = {
            'roster': [
                {
                    'name': 'player1'
                },
                {
                    'name': 'player2'
                },
                {
                    'name': 'player3'
                }
            ],
            'roster_backup': {
                1: {
                    'name': 'player1'
                },
                2: {
                    'name': 'player2'
                },
                3: {
                    'name': 'player3'
                }
            }
        }
        json_str = json.dumps(data)
        obj: Team = Team.from_json(json_str)

        assert type(obj.roster[0]) is Player and type(obj.roster_backup[1]) is Player

    def test_mixed(self):
        data = {
            'roster': [
                {
                    'name': 'player1'
                },
                {
                    'name': 'player2'
                },
                {
                    'name': 'player3'
                }
            ],
            'roster_backup': {
                1: 5,
                2: 3,
                3: 2
            }
        }
        json_str = json.dumps(data)
        obj: Team = Team.from_json(json_str)

        assert type(obj.roster[0]) is Player and type(obj.roster_backup[1]) is int

    def test_mixed_inverse(self):
        data = {
            'roster': [
                1,
                2,
                3
            ],
            'roster_backup': {
                1: {
                    'name': 'player1'
                },
                2: {
                    'name': 'player2'
                },
                3: {
                    'name': 'player3'
                }
            }
        }
        json_str = json.dumps(data)
        obj: Team = Team.from_json(json_str)

        assert type(obj.roster[0]) is int and type(obj.roster_backup[1]) is Player


@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class StrictBase:
    pass


@dataclass
class StrictLeft(StrictBase):
    left: int


@dataclass
class StrictRight(StrictBase):
    right: int


@dataclass
class StrictChildren(StrictBase):
    children: List[StrictLeft]


@dataclass
class StrictResponse(StrictBase):
    values: List[Union[StrictLeft, StrictChildren]]


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class IncludeWithoutCatchAll:
    value: int


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class IncludeMultipleCatchAll:
    value: int
    extra: CatchAll
    other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class IncludeInvalidCatchAll:
    value: int
    extra: CatchAll


@dataclass_json
@dataclass(eq=False)
class EqualToInput:
    right: int

    def __eq__(self, other):
        return other == {"right": self.right}


class DictSubclass(dict):
    pass


def collection_class(value_type):
    @dataclass_json
    @dataclass
    class Values:
        values: value_type

    return Values


def strict_alternatives():
    @dataclass
    class Left(StrictLeft):
        pass

    @dataclass
    class Right(StrictRight):
        pass

    return Left, Right


def decoded_candidate(decoder, undefined=Undefined.RAISE):
    @dataclass_json(undefined=undefined)
    @dataclass
    class Candidate:
        value: int = field(metadata=config(decoder=decoder))

    return Candidate


def payload_candidate(candidate, decoder=None):
    @dataclass_json(undefined=Undefined.RAISE)
    @dataclass
    class Payload:
        payload: candidate = field(metadata=config(decoder=decoder))

    return Payload


def recording_decoder(calls, error=None):
    def decode(value):
        calls.append(value)
        if error is not None:
            raise error
        return int(value)

    return decode


def capturing_decoder(candidate, errors):
    def decode(value):
        try:
            return candidate.from_dict(value)
        except UndefinedParameterError as error:
            errors.append(error)
            raise

    return decode


def failed_union_warning(value):
    return (f"Failed to decode {value} Union dataclasses."
            f"Expected Union to include a matching dataclass and it didn't.")


include_failures = [
    (IncludeWithoutCatchAll, {"value": "1"},
     "No field of type dataclasses_json.CatchAll defined"),
    (IncludeMultipleCatchAll, {"value": "1"},
     "Multiple catch-all fields supplied: 2."),
    (IncludeInvalidCatchAll, {"value": "1", "extra": "invalid"},
     "Received input field with same name as catch-all field: 'extra': 'invalid'"),
]


class TestStrictUnion:
    @pytest.mark.parametrize("entry", ["from_dict", "from_json"])
    @pytest.mark.parametrize("reverse", [False, True])
    @pytest.mark.parametrize("mapping", [False, True])
    def test_alternatives(self, entry, reverse, mapping):
        left, right = strict_alternatives()
        options = Union[right, left] if reverse else Union[left, right]
        value_type = Dict[str, options] if mapping else List[options]
        source = {"a": {"left": 1}, "b": {"right": 2}} if mapping else [{"left": 1}, {"right": 2}]
        expected = {"a": left(1), "b": right(2)} if mapping else [left(1), right(2)]
        data = {"values": source}
        argument = json.dumps(data) if entry == "from_json" else data
        result = getattr(collection_class(value_type), entry)(argument)
        assert result.values == expected
        assert type(result.values) is type(expected)

    @pytest.mark.parametrize("error_type", [UndefinedParameterError, TypeError, RuntimeError])
    def test_constructor_errors_are_immediate_original_objects(self, error_type):
        error = error_type("constructor rejection")

        @dataclass_json(undefined=Undefined.RAISE)
        @dataclass
        class ConstructorFailure:
            value: int

            def __post_init__(self):
                raise error

        later_calls = []
        later = decoded_candidate(recording_decoder(later_calls))
        with pytest.raises(error_type) as caught:
            collection_class(List[Union[ConstructorFailure, later]]).from_dict({"values": [{"value": "1"}]})
        assert caught.value is error
        assert later_calls == []

    def test_inheritance_repeated_calls_and_input(self):
        data = {"values": [{"left": 1}, {"children": [{"left": 2}]}]}
        original = deepcopy(data)
        expected = StrictResponse([StrictLeft(1), StrictChildren([StrictLeft(2)])])
        assert StrictResponse.from_dict(data) == expected
        assert StrictResponse.from_dict(data) == expected
        assert data == original

    def test_success_has_no_failed_union_warning(self):
        with warnings.catch_warnings(record=True) as seen:
            result = collection_class(List[Union[StrictLeft, StrictRight]]).from_dict(
                {"values": [{"right": 2}, {"left": 1}]})
        assert result.values == [StrictRight(2), StrictLeft(1)]
        assert seen == []

    @pytest.mark.parametrize("reverse", [False, True])
    def test_first_success_stops_callbacks(self, reverse):
        calls = []
        first = decoded_candidate(recording_decoder(calls))
        later_calls = []
        later = decoded_candidate(recording_decoder(later_calls))
        options = Union[later, first] if reverse else Union[first, later]
        result = collection_class(List[options]).from_dict({"values": [{"value": "1"}]})
        expected_type = later if reverse else first
        assert type(result.values[0]) is expected_type
        assert (calls, later_calls) == ([], ["1"]) if reverse else (calls, later_calls) == (["1"], [])

    def test_first_strict_error_contract(self):
        with warnings.catch_warnings(record=True) as seen:
            with pytest.raises(UndefinedParameterError) as caught:
                collection_class(List[Union[StrictLeft, StrictRight]]).from_dict(
                    {"values": [{"left": 1, "right": 2}]})
        message = "Received undefined initialization arguments {'right': 2}"
        assert type(caught.value) is UndefinedParameterError
        assert caught.value.args == (message,)
        assert str(caught.value) == message
        assert seen == []

    @pytest.mark.parametrize("error_type", [KeyError, ValueError, AttributeError])
    def test_ordinary_mismatch_then_strict_exhaustion(self, error_type):
        candidate = decoded_candidate(recording_decoder([], error_type("mismatch")))
        with warnings.catch_warnings(record=True) as seen:
            with pytest.raises(UndefinedParameterError) as caught:
                collection_class(List[Union[candidate, StrictLeft]]).from_dict(
                    {"values": [{"value": "1"}]})
        assert caught.value.args == ("Received undefined initialization arguments {'value': '1'}",)
        assert seen == []

    def test_nested_strict_failure_tries_later_candidate(self):
        first = payload_candidate(StrictLeft)
        later = payload_candidate(StrictRight)
        result = collection_class(List[Union[first, later]]).from_dict(
            {"values": [{"payload": {"right": 2}}]})
        assert type(result.values[0]) is later
        assert result.values[0].payload == StrictRight(2)

    def test_nested_strict_exhaustion_preserves_error_identity(self):
        errors = []
        first = payload_candidate(StrictLeft, capturing_decoder(StrictLeft, errors))
        later = payload_candidate(StrictRight, capturing_decoder(StrictRight, errors))
        with warnings.catch_warnings(record=True) as seen:
            with pytest.raises(UndefinedParameterError) as caught:
                collection_class(List[Union[first, later]]).from_dict(
                    {"values": [{"payload": {"left": 1, "right": 2}}]})
        assert caught.value is errors[0]
        assert len(errors) == 2
        assert caught.value.args == ("Received undefined initialization arguments {'right': 2}",)
        assert seen == []

    @pytest.mark.parametrize("candidate, value, message", include_failures)
    def test_include_errors_are_immediate(self, candidate, value, message):
        later_calls = []
        later = decoded_candidate(recording_decoder(later_calls), Undefined.EXCLUDE)
        with pytest.raises(UndefinedParameterError) as caught:
            collection_class(List[Union[candidate, later]]).from_dict({"values": [value]})
        assert type(caught.value) is UndefinedParameterError
        assert caught.value.args == (message,)
        assert str(caught.value) == message
        assert later_calls == []

    @pytest.mark.parametrize("candidate, value, message", include_failures)
    def test_nested_include_errors_preserve_identity(self, candidate, value, message):
        errors = []
        first = payload_candidate(candidate, capturing_decoder(candidate, errors))
        later_calls = []
        later_type = decoded_candidate(recording_decoder(later_calls), Undefined.EXCLUDE)
        later = payload_candidate(later_type)
        with pytest.raises(UndefinedParameterError) as caught:
            collection_class(List[Union[first, later]]).from_dict({"values": [{"payload": value}]})
        assert caught.value is errors[0]
        assert type(caught.value) is UndefinedParameterError
        assert caught.value.args == (message,)
        assert later_calls == []

    @pytest.mark.parametrize("error_type", [UndefinedParameterError, TypeError, RuntimeError])
    def test_user_errors_are_immediate_original_objects(self, error_type):
        error = error_type("custom rejection")
        first_calls = []
        first = decoded_candidate(recording_decoder(first_calls, error))
        later_calls = []
        later = decoded_candidate(recording_decoder(later_calls))
        with pytest.raises(error_type) as caught:
            collection_class(List[Union[first, later]]).from_dict({"values": [{"value": "1"}]})
        assert caught.value is error
        assert first_calls == ["1"]
        assert later_calls == []

    @pytest.mark.parametrize("error_type", [KeyError, ValueError, AttributeError])
    def test_ordinary_mismatch_tries_later_candidate(self, error_type):
        first = decoded_candidate(recording_decoder([], error_type("mismatch")))
        later_calls = []
        later = decoded_candidate(recording_decoder(later_calls))
        result = collection_class(List[Union[first, later]]).from_dict({"values": [{"value": "1"}]})
        assert type(result.values[0]) is later
        assert result.values[0].value == 1
        assert later_calls == ["1"]

    @pytest.mark.parametrize("strict", [False, True])
    def test_missing_only_exhaustion_preserves_dict_and_warning(self, strict):
        @dataclass_json
        @dataclass
        class Ordinary:
            absent: int

        first = StrictLeft if strict else Ordinary
        value = {}
        with pytest.warns(UserWarning) as seen:
            result = collection_class(List[Union[first, StrictRight]]).from_dict({"values": [value]})
        assert result.values[0] is value
        assert len(seen) == 1
        assert seen[0].category is UserWarning
        assert str(seen[0].message) == failed_union_warning(value)

    @pytest.mark.parametrize("error_type", [KeyError, ValueError, AttributeError])
    def test_ordinary_callback_exhaustion_preserves_warning(self, error_type):
        first = decoded_candidate(recording_decoder([], error_type("first")))
        later = decoded_candidate(recording_decoder([], error_type("later")))
        value = {"value": "1"}
        with pytest.warns(UserWarning) as seen:
            result = collection_class(List[Union[first, later]]).from_dict({"values": [value]})
        assert result.values[0] is value
        assert len(seen) == 1
        assert seen[0].category is UserWarning
        assert str(seen[0].message) == failed_union_warning(value)

    @pytest.mark.parametrize("value", [1, "text", DictSubclass(right=2), StrictRight(2)])
    def test_passthrough_values(self, value):
        with warnings.catch_warnings(record=True) as seen:
            result = collection_class(List[Union[StrictLeft, StrictRight, int, str]]).from_dict({"values": [value]})
        assert result.values[0] is value
        assert seen == []

    @pytest.mark.parametrize("reverse", [False, True])
    def test_explicit_dict_bypasses_candidates(self, reverse):
        options = Union[dict, StrictLeft] if reverse else Union[StrictLeft, dict]
        value = {"right": 2}
        with warnings.catch_warnings(record=True) as seen:
            result = collection_class(List[options]).from_dict({"values": [value]})
        assert result.values[0] is value
        assert seen == []

    @pytest.mark.parametrize("value_type, value", [(List[Any], {"right": 2}),
                                                  (List[Optional[StrictLeft]], None)])
    def test_any_and_none(self, value_type, value):
        with warnings.catch_warnings(record=True) as seen:
            result = collection_class(value_type).from_dict({"values": [value]})
        assert result.values[0] is value
        assert seen == []

    def test_optional_delegates_and_infers_missing(self):
        result = collection_class(List[Optional[StrictLeft]]).from_dict({"values": [{"left": 1}]})
        with pytest.warns(RuntimeWarning, match="infer_missing=True"):
            inferred = collection_class(List[Optional[StrictLeft]]).from_dict({"values": [{}]}, infer_missing=True)
        assert result.values == [StrictLeft(1)]
        assert inferred.values == [StrictLeft(None)]

    def test_success_equal_to_input_keeps_warning(self):
        value = {"right": 2}
        with pytest.warns(UserWarning) as seen:
            result = collection_class(List[Union[StrictLeft, EqualToInput]]).from_dict({"values": [value]})
        assert type(result.values[0]) is EqualToInput
        assert result.values[0].right == 2
        assert len(seen) == 1
        assert str(seen[0].message) == failed_union_warning(value)

    def test_standalone_strict_error_contract(self):
        with pytest.raises(UndefinedParameterError) as caught:
            StrictLeft.from_dict({"left": 1, "right": 2})
        message = "Received undefined initialization arguments {'right': 2}"
        assert type(caught.value) is UndefinedParameterError
        assert caught.value.args == (message,)
        assert str(caught.value) == message

    def test_later_decoder_runs_once_after_strict_failure(self):
        calls = []
        later = decoded_candidate(recording_decoder(calls))
        result = collection_class(List[Union[StrictLeft, later]]).from_dict({"values": [{"value": "1"}]})
        assert type(result.values[0]) is later
        assert result.values[0].value == 1
        assert calls == ["1"]

    def test_default_factory_is_not_repeated(self):
        calls = []

        def default_left():
            calls.append(1)
            return 1

        @dataclass_json(undefined=Undefined.RAISE)
        @dataclass
        class WithDefault:
            left: int = field(default_factory=default_left)

        result = collection_class(List[Union[WithDefault, StrictRight]]).from_dict({"values": [{"right": 2}]})
        assert result.values == [StrictRight(2)]
        assert calls == [1]
