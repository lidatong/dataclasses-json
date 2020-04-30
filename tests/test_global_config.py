from dataclasses import dataclass

from dataclasses_json import dataclass_json
from datetime import date
import dataclasses_json
import dataclasses_json.cfg


@dataclass_json
@dataclass
class Person:
    name: str


@dataclass_json
@dataclass
class PersonWithBirthday:
    name: str
    birthday: date


class TestGlobalConfig:
    def test_encoder_override(self):
        dataclasses_json.cfg.global_config.encoders[str] = lambda s: s[::-1]
        assert Person("Kobe Bryant").to_json() == '{"name": "tnayrB eboK"}'
        dataclasses_json.cfg.global_config.encoders = {}

    def test_encoder_extension(self):
        dataclasses_json.cfg.global_config.encoders[date] = date.isoformat
        assert PersonWithBirthday("Kobe Bryant", date(1978, 8, 23)).to_json() \
               == '{"name": "Kobe Bryant", "birthday": "1978-08-23"}'
        dataclasses_json.cfg.global_config.encoders = {}
