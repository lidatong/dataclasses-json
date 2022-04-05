from datetime import datetime, timezone
from dataclasses import dataclass, field
import sys

from marshmallow import fields
import pytest

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DataClassWithDatetime:
    created_at: datetime


if sys.version_info >= (3, 7):
    @dataclass_json
    @dataclass
    class DataClassWithIsoDatetime:
        created_at: datetime = field(
            metadata={'dataclasses_json': {
                'encoder': datetime.isoformat,
                'decoder': datetime.fromisoformat,
            }})


    @dataclass_json
    @dataclass
    class DataClassWithCustomIsoDatetime:
        created_at: datetime = field(
            metadata={'dataclasses_json': {
                'encoder': datetime.isoformat,
                'decoder': datetime.fromisoformat,
            }})


class TestTime:
    dt = datetime(2018, 11, 17, 16, 55, 28, 456753, tzinfo=timezone.utc)
    tz = timezone.utc

    ts = dt.timestamp()
    dc_ts_json = f'{{"created_at": {ts}}}'
    dc_ts = DataClassWithDatetime(datetime.fromtimestamp(ts, tz=tz))

    if sys.version_info >= (3, 7):
        iso = dt.isoformat()
        dc_iso_json = f'{{"created_at": "{iso}"}}'
        dc_iso = DataClassWithIsoDatetime(datetime.fromisoformat(iso))

    def test_datetime_encode(self):
        assert (self.dc_ts.to_json() == self.dc_ts_json)

    def test_datetime_decode(self):
        assert (DataClassWithDatetime.from_json(self.dc_ts_json) == self.dc_ts)

    @pytest.mark.skipif(sys.version_info < (3, 7),
                        reason="requires python3.7")
    def test_datetime_override_encode(self):
        assert (self.dc_iso.to_json() == self.dc_iso_json)

    @pytest.mark.skipif(sys.version_info < (3, 7),
                        reason="requires python3.7")
    def test_datetime_override_decode(self):
        assert (DataClassWithIsoDatetime.from_json(
            self.dc_iso_json) == self.dc_iso)
