from typing import Dict, Union, Any
import pytest

from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class DataWithDict:
    metadata: Dict[Any, Any]


@dataclass_json
@dataclass(frozen=True)
class DataWithTypedDict:
    metadata: Dict[str, Union[str, float]]


@dataclass_json
@dataclass(frozen=True)
class DataWithPythonDict:
    metadata: dict


example_metadata_dict = {"some_data": "written_here", "some_score": 34.4}
d_ex_1 = DataWithDict(metadata=example_metadata_dict)
d_ex_2 = DataWithTypedDict(metadata=example_metadata_dict)
d_ex_3 = DataWithPythonDict(metadata=example_metadata_dict)
d_ex_as_dict = {"metadata": example_metadata_dict}


class TestEncoder:
    def test_dataclass_with_dict(self):
        assert d_ex_1.to_dict() == d_ex_as_dict, f'Actual: {d_ex_1.to_dict()}, Expected: {d_ex_as_dict}'

    def test_dataclass_with_typed_dict(self):
        assert d_ex_2.to_dict() == d_ex_as_dict, f'Actual: {d_ex_2.to_dict()}, Expected: {d_ex_as_dict}'

    def test_dataclass_with_python_dict(self):
        assert d_ex_3.to_dict() == d_ex_as_dict, f'Actual: {d_ex_3.to_dict()}, Expected: {d_ex_as_dict}'


class TestDecoder:
    def test_dataclass_with_dict(self):
        d_from_dict = DataWithDict.from_dict(d_ex_as_dict)
        assert d_ex_1 == d_from_dict, f'Actual: {d_from_dict}, Expected: {d_ex_1}'

    def test_dataclass_with_typed_dict(self):
        d_from_dict = DataWithTypedDict.from_dict(d_ex_as_dict)
        assert d_ex_2 == d_from_dict, f'Actual: {d_from_dict}, Expected: {d_ex_2}'

    def test_dataclass_with_python_dict(self):
        d_from_dict = DataWithPythonDict.from_dict(d_ex_as_dict)
        assert d_ex_3 == d_from_dict, f'Actual: {d_from_dict}, Expected: {d_ex_3}'


class TestValidator:
    @pytest.mark.parametrize('metadata_dict, is_valid', [
        ({}, True),
        (example_metadata_dict, True),
        ({"is_boolean": True}, True),
        (None, False)
    ])
    def test_dataclass_with_dict(self, metadata_dict, is_valid):
        schema = DataWithDict.schema()
        res = schema.validate({"metadata": metadata_dict})
        assert not res == is_valid

    @pytest.mark.parametrize('metadata_dict, is_valid', [
        ({}, True),
        (example_metadata_dict, True),
        ({"is_boolean": True}, False),
        ({5: "a number"}, False)
    ])
    def test_dataclass_with_typed_dict(self, metadata_dict, is_valid):
        schema = DataWithTypedDict.schema()
        res = schema.validate({"metadata": metadata_dict})
        assert not res == is_valid

    @pytest.mark.parametrize('metadata_dict, is_valid', [
        ({}, True),
        (example_metadata_dict, True),
        ({"is_boolean": True}, True),
        (None, False)
    ])
    def test_dataclass_with_python_dict(self, metadata_dict, is_valid):
        schema = DataWithPythonDict.schema()
        res = schema.validate({"metadata": metadata_dict})
        assert not res == is_valid
