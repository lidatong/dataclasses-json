"""Test dataclasses_json handling of Literal types."""
import sys
import pytest

if sys.version_info < (3, 8):
    pytest.skip("Literal types are only supported in Python 3.8+", allow_module_level=True)

import json
from typing import Literal, Optional, List, Dict

from dataclasses import dataclass

from dataclasses_json import dataclass_json, DataClassJsonMixin
from marshmallow.exceptions import ValidationError  # type: ignore


@dataclass_json
@dataclass
class DataClassWithLiteral(DataClassJsonMixin):
    numeric_literals: Literal[0, 1]
    string_literals: Literal["one", "two", "three"]
    mixed_literals: Literal[0, "one", 2]


with_valid_literal_json = '{"numeric_literals": 0, "string_literals": "one", "mixed_literals": 2}'
with_valid_literal_data = DataClassWithLiteral(numeric_literals=0, string_literals="one", mixed_literals=2)
with_invalid_literal_json = '{"numeric_literals": 9, "string_literals": "four", "mixed_literals": []}'
with_invalid_literal_data = DataClassWithLiteral(numeric_literals=9, string_literals="four", mixed_literals=[])  # type: ignore

@dataclass_json
@dataclass
class DataClassWithNestedLiteral(DataClassJsonMixin):
    list_of_literals: List[Literal[0, 1]]
    dict_of_literals: Dict[Literal["one", "two", "three"], Literal[0, 1]]
    optional_literal: Optional[Literal[0, 1]]

with_valid_nested_literal_json = '{"list_of_literals": [0, 1], "dict_of_literals": {"one": 0, "two": 1}, "optional_literal": 1}'
with_valid_nested_literal_data = DataClassWithNestedLiteral(list_of_literals=[0, 1], dict_of_literals={"one": 0, "two": 1}, optional_literal=1)
with_invalid_nested_literal_json = '{"list_of_literals": [0, 2], "dict_of_literals": {"one": 0, "four": 2}, "optional_literal": 2}'
with_invalid_nested_literal_data = DataClassWithNestedLiteral(list_of_literals=[0, 2], dict_of_literals={"one": 0, "four": 2}, optional_literal=2)  # type: ignore

class TestEncoder:
    def test_valid_literal(self):
        assert with_valid_literal_data.to_dict(encode_json=True) == json.loads(with_valid_literal_json)
    
    def test_invalid_literal(self):
        assert with_invalid_literal_data.to_dict(encode_json=True) == json.loads(with_invalid_literal_json)

    def test_valid_nested_literal(self):
        assert with_valid_nested_literal_data.to_dict(encode_json=True) == json.loads(with_valid_nested_literal_json)

    def test_invalid_nested_literal(self):
        assert with_invalid_nested_literal_data.to_dict(encode_json=True) == json.loads(with_invalid_nested_literal_json)
        

class TestSchemaEncoder:
    def test_valid_literal(self):
        actual = DataClassWithLiteral.schema().dumps(with_valid_literal_data)
        assert json.loads(actual) == json.loads(with_valid_literal_json)

    def test_invalid_literal(self):
        actual = DataClassWithLiteral.schema().dumps(with_invalid_literal_data)
        assert json.loads(actual) == json.loads(with_invalid_literal_json)

    def test_valid_nested_literal(self):
        actual = DataClassWithNestedLiteral.schema().dumps(with_valid_nested_literal_data)
        assert json.loads(actual) == json.loads(with_valid_nested_literal_json)

    def test_invalid_nested_literal(self):
        actual = DataClassWithNestedLiteral.schema().dumps(with_invalid_nested_literal_data)
        assert json.loads(actual) == json.loads(with_invalid_nested_literal_json)

class TestDecoder:
    def test_valid_literal(self):
        actual = DataClassWithLiteral.from_json(with_valid_literal_json)
        assert actual == with_valid_literal_data

    def test_invalid_literal(self):
        expected = DataClassWithLiteral(numeric_literals=9, string_literals="four", mixed_literals=[])  # type: ignore
        actual = DataClassWithLiteral.from_json(with_invalid_literal_json)
        assert actual == expected


class TestSchemaDecoder:
    def test_valid_literal(self):
        actual = DataClassWithLiteral.schema().loads(with_valid_literal_json)
        assert actual == with_valid_literal_data

    def test_invalid_literal(self):
        with pytest.raises(ValidationError):
            DataClassWithLiteral.schema().loads(with_invalid_literal_json)

    def test_valid_nested_literal(self):
        actual = DataClassWithNestedLiteral.schema().loads(with_valid_nested_literal_json)
        assert actual == with_valid_nested_literal_data

    def test_invalid_nested_literal(self):
        with pytest.raises(ValidationError):
            DataClassWithNestedLiteral.schema().loads(with_invalid_nested_literal_json)
