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
class NotWorkingDictUnion:
    d: Dict[str, Union[TestChild, TestOtherChild]]


@dataclass_json
@dataclass(frozen=True)
class NotWorkingListUnion:
    l: List[Union[TestChild, TestOtherChild]]


class TestCollectionOfUnions:
    def test_dict(self):
        data = {
            "d": {
                "child" : {
                    "some_field" : 1
                },
                "other_child" : {
                    "other_field" : 2
                }
            }
        }
        json_str = json.dumps(data)
        obj = NotWorkingDictUnion.from_json(json_str)

        assert type(obj.d['child']) in (TestChild, TestOtherChild)

    def test_list(self):
        data = {
            "l": [
                {
                    "some_field" : 1
                },
                {
                    "other_field" : 1
                }
            ]
        }
        json_str = json.dumps(data)
        obj = NotWorkingListUnion.from_json(json_str)

        assert type(obj.l[0]) in (TestChild, TestOtherChild)
