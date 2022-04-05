import sys
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import pytest

from tests.entities import (DataClassBoolImmutableDefault,
                            DataClassIntImmutableDefault,
                            DataClassJsonDecorator,
                            DataClassWithConfigDecorator,
                            DataClassWithConfigHelper,
                            DataClassWithDataClass,
                            DataClassWithDecimal, DataClassWithList,
                            DataClassWithNestedNewType, DataClassWithNewType,
                            DataClassWithOptional,
                            DataClassWithOptionalDatetime,
                            DataClassWithOptionalDecimal,
                            DataClassWithOptionalNested,
                            DataClassWithOptionalUuid, DataClassWithUuid, UUIDWrapper,
                            UUIDWrapperWrapper)


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
        assert (DataClassWithNewType(UUIDWrapper(UUID(self.new_type_s))).to_json()
                == self.dc_new_type_json)

    @pytest.mark.skipif(sys.version_info >= (3, 10),
                        reason="newtype decode breaks in 3.10")
    def test_new_type_decode(self):
        assert (DataClassWithNewType.from_json(self.dc_new_type_json)
                == DataClassWithNewType(UUIDWrapper(UUID(self.new_type_s))))

    def test_nested_new_type_encode(self):
        assert (DataClassWithNestedNewType(
            UUIDWrapperWrapper(UUIDWrapper(UUID(self.new_type_s)))).to_json()
                == self.dc_new_type_json)

    @pytest.mark.skipif(sys.version_info >= (3, 10),
                        reason="newtype decode breaks in 3.10")
    def test_nested_new_type_decode(self):
        assert (DataClassWithNestedNewType.from_json(self.dc_new_type_json)
                == DataClassWithNestedNewType(
                    UUIDWrapperWrapper(UUIDWrapper(UUID(self.new_type_s)))))


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


class TestOverride:
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
