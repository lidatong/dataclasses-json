from datetime import datetime, timezone
from dataclasses import dataclass, field
import sys

from marshmallow import fields
import pytest

from dataclasses_json import dataclass_json
from dataclasses_json.mm import _IsoField


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
                'mm_field': fields.DateTime(format='iso')
            }})


    @dataclass_json
    @dataclass
    class DataClassWithCustomIsoDatetime:
        created_at: datetime = field(
            metadata={'dataclasses_json': {
                'encoder': datetime.isoformat,
                'decoder': datetime.fromisoformat,
                'mm_field': _IsoField()
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

    def test_datetime_schema_encode(self):
        assert (DataClassWithDatetime.schema().dumps(self.dc_ts)
                == self.dc_ts_json)

    def test_datetime_schema_decode(self):
        assert (DataClassWithDatetime.schema().loads(self.dc_ts_json)
                == self.dc_ts)

    @pytest.mark.skipif(sys.version_info < (3, 7),
                        reason="requires python3.7")
    def test_datetime_override_schema_encode(self):
        assert (DataClassWithIsoDatetime.schema().dumps(self.dc_iso)
                == self.dc_iso_json)

    @pytest.mark.skipif(sys.version_info < (3, 7),
                        reason="requires python3.7")
    def test_datetime_override_schema_decode(self):
        iso = DataClassWithIsoDatetime.schema().loads(self.dc_iso_json)
        # FIXME bug in marshmallow currently returns datetime-naive instead of
        # datetime-aware. also seems to drop microseconds?
        # #955
        iso.created_at = iso.created_at.replace(microsecond=456753,
                                                tzinfo=self.tz)
        assert (iso == self.dc_iso)

    @pytest.mark.skipif(sys.version_info < (3, 7),
                        reason="requires python3.7")
    def test_datetime_custom_iso_fieldoverride_schema_encode(self):
        assert (DataClassWithCustomIsoDatetime.schema().dumps(self.dc_iso)
                == self.dc_iso_json)

    @pytest.mark.skipif(sys.version_info < (3, 7),
                        reason="requires python3.7")
    def test_datetime_custom_iso_field_override_schema_decode(self):
        iso = DataClassWithCustomIsoDatetime.schema().loads(self.dc_iso_json)
        assert (iso == DataClassWithCustomIsoDatetime(self.dt))
