import datetime
import json
from dataclasses import dataclass, field

import pytest
from marshmallow import fields

from dataclasses_json import LetterCase, Undefined, config, dataclass_json


@pytest.mark.parametrize('many', [False, True])
@pytest.mark.parametrize('class_case,field_options,json_key', [
    (LetterCase.CAMEL, {}, 'openTime'),
    (None, {'letter_case': LetterCase.CAMEL}, 'openTime'),
    (None, {'field_name': 'opens'}, 'opens'),
])
def test_custom_mm_field_uses_configured_json_key(class_case, field_options, json_key, many):
    mm_field = fields.Time(format='%H:%M:%S')

    @dataclass_json(letter_case=class_case, undefined=Undefined.EXCLUDE)
    @dataclass
    class Store:
        open_time: datetime.time = field(metadata=config(mm_field=mm_field, **field_options))

    store = Store(datetime.time(3))
    payload = {json_key: '03:00:00'}
    expected = [store] if many else store
    data = [payload] if many else payload
    schema = Store.schema(many=many)

    assert schema.loads(json.dumps(data)) == expected
    assert schema.dump(expected) == data
    assert mm_field.data_key is None


def test_custom_mm_field_explicit_data_key_takes_precedence():
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class Store:
        open_time: datetime.time = field(metadata=config(
            mm_field=fields.Time(format='%H:%M:%S', data_key='opens'),
        ))

    store = Store(datetime.time(3))
    schema = Store.schema()

    assert schema.load({'opens': '03:00:00'}) == store
    assert schema.dump(store) == {'opens': '03:00:00'}


def test_custom_mm_field_can_be_shared_between_different_json_keys():
    mm_field = fields.String()

    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class Record:
        first_name: str = field(metadata=config(mm_field=mm_field))
        last_name: str = field(metadata=config(mm_field=mm_field))

    schema = Record.schema()
    payload = {'firstName': 'Ada', 'lastName': 'Lovelace'}

    assert schema.load(payload) == Record('Ada', 'Lovelace')
    assert schema.dump(Record('Ada', 'Lovelace')) == payload
    assert mm_field.data_key is None
