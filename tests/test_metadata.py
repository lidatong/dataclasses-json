import datetime
from dataclasses import dataclass, field
from typing import Optional

import pytest
from marshmallow import fields, ValidationError

from dataclasses_json import DataClassJsonMixin


@dataclass
class Car(DataClassJsonMixin):
    license_number: str = field(
        metadata={'dataclasses_json': {
            'mm_field': fields.String(required=False)}
        })


@dataclass
class StringDate(DataClassJsonMixin):
    string_date: datetime.datetime = field(
        metadata={'dataclasses_json': {
            'encoder': str,
            'decoder': str,
            'mm_field': fields.String(required=False)}
        })
    
@dataclass
class OptionalStringDate(DataClassJsonMixin):
    string_date: Optional[datetime.datetime] = field(
        default=None,
        metadata={'dataclasses_json': {
            'encoder': str,
            'decoder': str,
            'mm_field': fields.String(required=False)}
        })


car_schema = Car.schema()
string_date_schema = StringDate.schema()
opt_string_date_schema = OptionalStringDate.schema()


class TestMetadata:
    def test_validation_error_raises(self):
        with pytest.raises(ValidationError) as e:
            car_schema.load({'license_number': 123})
        assert e.value.messages == {'license_number': ['Not a valid string.']}

    def test_mm_field_takes_precedence_over_types(self):
        obj = string_date_schema.load({'string_date': 'yesterday'})
        assert isinstance(obj, StringDate)
        assert obj.string_date == 'yesterday'

    def test_optional_field_only_decoded_when_present(self):
        obj = opt_string_date_schema.load({})
        assert isinstance(obj, OptionalStringDate)
        assert obj.string_date == None
        
        another_obj = opt_string_date_schema.load({'string_date': 'today'})
        assert isinstance(another_obj, OptionalStringDate)
        assert another_obj.string_date == 'today'
