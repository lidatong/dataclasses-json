from dataclasses import dataclass
from typing import Dict, Union, List
import json

from dataclasses_json import dataclass_json


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
    roster: list[Union[int, Player]]
    roster_backup: dict[int, Union[int, Player]]


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
