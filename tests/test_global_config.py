from dataclasses import dataclass
from typing import List, Optional

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


@dataclass_json
@dataclass
class HistoricalEvents:
    dates: List[date]


@dataclass_json
@dataclass
class PackageDelivery:
    date: Optional[date]


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

    def test_encoder_and_decoder_extension_in_collections(self):
        dataclasses_json.cfg.global_config.encoders[date] = date.isoformat
        dataclasses_json.cfg.global_config.decoders[date] = date.fromisoformat
        historical_events = HistoricalEvents([date(1918, 11, 11), date(1945, 5, 8)])
        expected_json = '{"dates": ["1918-11-11", "1945-05-08"]}'
        assert historical_events.to_json() == expected_json
        assert HistoricalEvents.from_json(expected_json) == historical_events
        dataclasses_json.cfg.global_config.encoders = {}
        dataclasses_json.cfg.global_config.decoders = {}

    def test_encoder_and_decoder_extension_in_union(self):
        dataclasses_json.cfg.global_config.encoders[date] = date.isoformat
        dataclasses_json.cfg.global_config.decoders[date] = date.fromisoformat
        package_delivery = PackageDelivery(date(2023, 1, 1))
        expected_json = '{"date": "2023-01-01"}'
        assert package_delivery.to_json() == expected_json
        assert PackageDelivery.from_json(expected_json) == package_delivery
        dataclasses_json.cfg.global_config.encoders = {}
        dataclasses_json.cfg.global_config.decoders = {}
