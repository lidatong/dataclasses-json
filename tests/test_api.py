from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import pytest

from tests.entities import (DataClassBoolImmutableDefault,
                            DataClassIntImmutableDefault,
                            DataClassJsonDecorator,
                            DataClassWithConfigDecorator,
                            DataClassWithConfigHelper,
                            DataClassWithConfigManual, DataClassWithDataClass,
                            DataClassWithDecimal, DataClassWithList,
                            DataClassWithNestedNewType, DataClassWithNewType,
                            DataClassWithOptional,
                            DataClassWithOptionalDatetime,
                            DataClassWithOptionalDecimal,
                            DataClassWithOptionalNested,
                            DataClassWithOptionalUuid, DataClassWithUuid, Id,
                            ProductId)


class TestTypes:
    decimal_s = "12345.12345"
    dc_decimal_json = f'{{"x": "{decimal_s}"}}'

    uuid_s = 'd1d61dd7-c036-47d3-a6ed-91cc2e885fc8'
    dc_uuid_json = f'{{"id": "{uuid_s}"}}'

    def test_decimal_encode(self):
        assert (DataClassWithDecimal(Decimal(self.decimal_s)).to_json()
                == self.dc_decimal_json)

    def test_decimal_decode(self):
        assert (DataClassWithDecimal.from_json(self.dc_decimal_json)
                == DataClassWithDecimal(Decimal(self.decimal_s)))


class TestGenericExtendedTypes:
    def test_optional_datetime(self):
        dt = datetime(2018, 11, 17, 16, 55, 28, 456753, tzinfo=timezone.utc)
        dc = DataClassWithOptionalDatetime(dt)
        assert (DataClassWithOptionalDatetime.from_json(dc.to_json())
                == dc)

    def test_optional_decimal(self):
        dc = DataClassWithOptionalDecimal(Decimal("12345.12345"))
        assert (DataClassWithOptionalDecimal.from_json(dc.to_json())
                == dc)

    def test_optional_uuid(self):
        dc = DataClassWithOptionalUuid(
            UUID('d1d61dd7-c036-47d3-a6ed-91cc2e885fc8'))
        assert (DataClassWithOptionalUuid.from_json(dc.to_json())
                == dc)


class TestDictDecode:
    decimal_s = "12345.12345"
    dc_decimal_json = {"x": decimal_s}

    uuid_s = 'd1d61dd7-c036-47d3-a6ed-91cc2e885fc8'
    dc_uuid_json = {"id": uuid_s}

    def test_decimal_decode(self):
        assert (DataClassWithDecimal.from_dict(self.dc_decimal_json)
                == DataClassWithDecimal(Decimal(self.decimal_s)))

    def test_uuid_decode(self):
        assert (DataClassWithUuid.from_dict(self.dc_uuid_json)
                == DataClassWithUuid(UUID(self.uuid_s)))


class TestNewType:
    new_type_s = 'd1d61dd7-c036-47d3-a6ed-91cc2e885fc8'
    dc_new_type_json = f'{{"id": "{new_type_s}"}}'

    def test_new_type_encode(self):
        assert (DataClassWithNewType(Id(UUID(self.new_type_s))).to_json()
                == self.dc_new_type_json)

    def test_new_type_decode(self):
        assert (DataClassWithNewType.from_json(self.dc_new_type_json)
                == DataClassWithNewType(Id(UUID(self.new_type_s))))

    def test_nested_new_type_encode(self):
        assert (DataClassWithNestedNewType(
            ProductId(Id(UUID(self.new_type_s)))).to_json()
                == self.dc_new_type_json)

    def test_nested_new_type_decode(self):
        assert (DataClassWithNestedNewType.from_json(self.dc_new_type_json)
                == DataClassWithNestedNewType(
                    ProductId(Id(UUID(self.new_type_s)))))


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
        assert DataClassBoolImmutableDefault.schema().dumps(
            d_bool) == '{"x": false}'

    def test_dumps_default_many(self):
        d_int = DataClassIntImmutableDefault()
        assert d_int.x == 0
        assert DataClassIntImmutableDefault.schema().dumps([d_int],
                                                           many=True) == '[{"x": 0}]'
        d_bool = DataClassBoolImmutableDefault()
        assert d_bool.x is False
        assert DataClassBoolImmutableDefault.schema().dumps([d_bool],
                                                            many=True) == '[{"x": false}]'

    def test_dumps_new_type(self):
        raw_value = 'd1d61dd7-c036-47d3-a6ed-91cc2e885fc8'
        id_value = Id(UUID(raw_value))

        d_new_type = DataClassWithNewType(id_value)

        assert DataClassWithNewType.schema().dumps(
            d_new_type) == f'{{"id": "{raw_value}"}}'

    def test_dumps_nested_new_type(self):
        raw_value = 'd1d61dd7-c036-47d3-a6ed-91cc2e885fc8'
        id_value = ProductId(Id(UUID(raw_value)))

        d_new_type = DataClassWithNestedNewType(id_value)

        assert DataClassWithNestedNewType.schema().dumps(
            d_new_type) == f'{{"id": "{raw_value}"}}'

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
        dc = DataClassWithConfigManual(5.0)
        assert dc.to_json() == '{"id": 5.0}'
        assert DataClassWithConfigManual.schema().dumps(dc) == '{"id": 5}'

    def test_override_with_config_helper(self):
        dc = DataClassWithConfigHelper(5.0)
        assert dc.to_json() == '{"id": "5.0"}'


class TestConfig:
    def test_config_encode(self):
        dc = DataClassWithConfigDecorator('a')
        assert dc.to_json() == '{"idField": "a"}'

    def test_config_decode(self):
        dc = DataClassWithConfigDecorator('a')
        assert DataClassWithConfigDecorator.from_json('{"idField": "a"}') == dc
