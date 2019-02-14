from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

import pytest

from tests.entities import (DataClassIntImmutableDefault, DataClassJsonDecorator,
                            DataClassWithDataClass, DataClassWithDatetime,
                            DataClassWithList, DataClassWithOptional,
                            DataClassWithOptionalNested, DataClassWithUuid,
                            DataClassWithIsoDatetime, DataClassWithOverride,
                            DataClassWithDecimal, DataClassWithCustomIsoDatetime,
                            DataClassBoolImmutableDefault)


class TestTypes:
    uuid_s = 'd1d61dd7-c036-47d3-a6ed-91cc2e885fc8'
    dc_uuid_json = f'{{"id": "{uuid_s}"}}'

    def test_uuid_encode(self):
        assert (DataClassWithUuid(UUID(self.uuid_s)).to_json()
                == self.dc_uuid_json)

    def test_uuid_decode(self):
        assert (DataClassWithUuid.from_json(self.dc_uuid_json)
                == DataClassWithUuid(UUID(self.uuid_s)))

    dt = datetime(2018, 11, 17, 16, 55, 28, 456753, tzinfo=timezone.utc)
    tz = timezone.utc

    ts = dt.timestamp()
    dc_ts_json = f'{{"created_at": {ts}}}'
    dc_ts = DataClassWithDatetime(datetime.fromtimestamp(ts, tz=tz))

    iso = dt.isoformat()
    dc_iso_json = f'{{"created_at": "{iso}"}}'
    dc_iso = DataClassWithIsoDatetime(datetime.fromisoformat(iso))

    dec = Decimal("0.04")
    dec_ts_json_in = f'{{"price": "{dec}"}}'
    dec_ts_json_out = f'{{"price": {dec}}}'
    dec_ts = DataClassWithDecimal(dec)

    def test_decimal_encode(self):
        assert self.dec_ts.to_json() == self.dec_ts_json_out

    def test_decimal_decode(self):
        assert DataClassWithDecimal.from_json(self.dec_ts_json_in) == self.dec_ts

    def test_datetime_encode(self):
        assert (self.dc_ts.to_json() == self.dc_ts_json)

    def test_datetime_decode(self):
        assert (DataClassWithDatetime.from_json(self.dc_ts_json) == self.dc_ts)

    def test_datetime_override_encode(self):
        assert (self.dc_iso.to_json() == self.dc_iso_json)

    def test_datetime_override_decode(self):
        assert (DataClassWithIsoDatetime.from_json(
            self.dc_iso_json) == self.dc_iso)

    def test_datetime_schema_encode(self):
        assert (DataClassWithDatetime.schema().dumps(self.dc_ts)
                == self.dc_ts_json)

    def test_datetime_schema_decode(self):
        assert (DataClassWithDatetime.schema().loads(self.dc_ts_json)
                == self.dc_ts)

    def test_datetime_override_schema_encode(self):
        assert (DataClassWithIsoDatetime.schema().dumps(self.dc_iso)
                == self.dc_iso_json)

    def test_datetime_override_schema_decode(self):
        iso = DataClassWithIsoDatetime.schema().loads(self.dc_iso_json)
        # FIXME bug in marshmallow currently returns datetime-naive instead of
        # datetime-aware. also seems to drop microseconds?
        # #955
        iso.created_at = iso.created_at.replace(microsecond=456753,
                                                tzinfo=self.tz)
        assert (iso == self.dc_iso)

    def test_datetime_custom_iso_fieldoverride_schema_encode(self):
        assert (DataClassWithCustomIsoDatetime.schema().dumps(self.dc_iso)
                == self.dc_iso_json)

    def test_datetime_custom_iso_field_override_schema_decode(self):
        iso = DataClassWithCustomIsoDatetime.schema().loads(self.dc_iso_json)
        assert (iso == DataClassWithCustomIsoDatetime(self.dt))


class TestInferMissing:
    def test_infer_missing(self):
        actual = DataClassWithOptional.from_json('{}', infer_missing=True)
        assert (actual == DataClassWithOptional(None))

    def test_infer_missing_is_recursive(self):
        actual = DataClassWithOptionalNested.from_json('{"x": {}}',
                                                       infer_missing=True)
        expected = DataClassWithOptionalNested(DataClassWithOptional(None))
        assert (actual == expected)

    def test_infer_missing_terminates_at_first_missing(self):
        actual = DataClassWithOptionalNested.from_json('{"x": null}',
                                                       infer_missing=True)
        assert (actual == DataClassWithOptionalNested(None))


class TestWarnings:
    def test_warns_when_nonoptional_field_is_missing_with_infer_missing(self):
        with pytest.warns(RuntimeWarning, match='Missing value'):
            actual = DataClassWithDataClass.from_json('{"dc_with_list": {}}',
                                                      infer_missing=True)
            expected = DataClassWithDataClass(DataClassWithList(None))
            assert (actual == expected)

    def test_warns_when_required_field_is_none(self):
        with pytest.warns(RuntimeWarning, match='`NoneType` object'):
            assert (DataClassWithDataClass.from_json(
                '{"dc_with_list": null}') == DataClassWithDataClass(None))


class TestErrors:
    def test_error_when_nonoptional_field_is_missing(self):
        with pytest.raises(KeyError):
            actual = DataClassWithDataClass.from_json('{"dc_with_list": {}}')
            expected = DataClassWithDataClass(DataClassWithList(None))
            assert (actual == expected)


class TestDecorator:
    def test_decorator(self):
        json_s = '{"x": "x"}'
        assert DataClassJsonDecorator.from_json(json_s).to_json() == json_s


class TestSchema:
    def test_dumps_many(self):
        actual = DataClassWithList.schema().dumps([DataClassWithList([1])],
                                                  many=True)
        json_s = '[{"xs": [1]}]'
        assert actual == json_s

    def test_dumps_many_nested(self):
        dumped = DataClassWithDataClass.schema().dumps(
            [DataClassWithDataClass(DataClassWithList([1]))],
            many=True)
        json_s = '[{"dc_with_list": {"xs": [1]}}]'
        assert dumped == json_s

    def test_loads_many(self):
        json_s = '[{"xs": [1]}]'
        assert (DataClassWithList.schema().loads(json_s, many=True)
                == [DataClassWithList([1])])

    def test_loads_many_nested(self):
        json_s = '[{"dc_with_list": {"xs": [1]}}]'
        assert (DataClassWithDataClass.schema().loads(json_s, many=True)
                == [DataClassWithDataClass(DataClassWithList([1]))])

    def test_loads_default(self):
        assert (DataClassIntImmutableDefault.schema().loads('{}')
                == DataClassIntImmutableDefault())
        assert (DataClassBoolImmutableDefault.schema().loads('{}')
                == DataClassBoolImmutableDefault())

    def test_loads_default_many(self):
        assert (DataClassIntImmutableDefault.schema().loads('[{}]', many=True)
                == [DataClassIntImmutableDefault()])
        assert (DataClassBoolImmutableDefault.schema().loads('[{}]', many=True)
                == [DataClassBoolImmutableDefault()])

    def test_dumps_default(self):
        d_int = DataClassIntImmutableDefault()
        assert d_int.x == 0
        assert DataClassIntImmutableDefault.schema().dumps(d_int) == '{"x": 0}'
        d_bool = DataClassBoolImmutableDefault()
        assert d_bool.x is False
        assert DataClassBoolImmutableDefault.schema().dumps(d_bool) == '{"x": false}'

    def test_dumps_default_many(self):
        d_int = DataClassIntImmutableDefault()
        assert d_int.x == 0
        assert DataClassIntImmutableDefault.schema().dumps([d_int], many=True) == '[{"x": 0}]'
        d_bool = DataClassBoolImmutableDefault()
        assert d_bool.x is False
        assert DataClassBoolImmutableDefault.schema().dumps([d_bool], many=True) == '[{"x": false}]'

    def test_loads_infer_missing(self):
        assert (DataClassWithOptional
                .schema(infer_missing=True)
                .loads('[{}]', many=True) == [DataClassWithOptional(None)])

    def test_loads_infer_missing_nested(self):
        assert (DataClassWithOptionalNested
                .schema(infer_missing=True)
                .loads('[{}]', many=True) == [
                    DataClassWithOptionalNested(None)])


class TestOverride:
    def test_override(self):
        dc = DataClassWithOverride(5.0)
        assert dc.to_json() == '{"id": 5.0}'
        assert DataClassWithOverride.schema().dumps(dc) == '{"id": 5}'
