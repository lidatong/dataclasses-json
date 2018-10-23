import pytest

from tests.entities import (DataClassJsonDecorator, DataClassWithDataClass,
                            DataClassWithList, DataClassWithOptional,
                            DataClassWithOptionalRecursive)


class TestInferMissing:
    def test_infer_missing(self):
        actual = DataClassWithOptional.from_json('{}', infer_missing=True)
        assert (actual == DataClassWithOptional(None))

    def test_infer_missing_is_recursive(self):
        actual = DataClassWithOptionalRecursive.from_json('{"x": {}}',
                                                          infer_missing=True)
        expected = DataClassWithOptionalRecursive(DataClassWithOptional(None))
        assert (actual == expected)

    def test_infer_missing_terminates_at_first_missing(self):
        actual = DataClassWithOptionalRecursive.from_json('{"x": null}',
                                                          infer_missing=True)
        assert (actual == DataClassWithOptionalRecursive(None))


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
