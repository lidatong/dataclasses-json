from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Person:
    name: str


class TestGlobalConfig:
    def test_json_module(self):
        assert Person("lidatong").to_json() == '{"name": "lidatong"}'
