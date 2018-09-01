import pytest

from tests.entities import (DataClassWithDataClass, DataClassWithList,
                            DataClassWithOptional,
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
            actual = DataClassWithDataClass.from_json('{"xs": {}}',
                                                      infer_missing=True)
            expected = DataClassWithDataClass(DataClassWithList(None))
            assert (actual == expected)

    def test_warns_when_required_field_is_none(self):
        with pytest.warns(RuntimeWarning, match='None value'):
            assert (DataClassWithDataClass.from_json('{"xs": null}') ==
                    DataClassWithDataClass(None))


class TestErrors:
    def test_error_when_nonoptional_field_is_missing(self):
        with pytest.raises(KeyError):
            actual = DataClassWithDataClass.from_json('{"xs": {}}')
            expected = DataClassWithDataClass(DataClassWithList(None))
            assert (actual == expected)
