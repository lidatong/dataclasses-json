from dataclasses import dataclass, field

from dataclasses_json import LetterCase, dataclass_json, config


@dataclass_json
@dataclass
class CamelCasePerson:
    given_name: str = field(
        metadata={'dataclasses_json': {
            'letter_case': LetterCase.CAMEL
        }}
    )


@dataclass_json
@dataclass
class KebabCasePerson:
    given_name: str = field(
        metadata={'dataclasses_json': {
            'letter_case': LetterCase.KEBAB
        }}
    )


@dataclass_json
@dataclass
class SnakeCasePerson:
    given_name: str = field(
        metadata={'dataclasses_json': {
            'letter_case': LetterCase.SNAKE
        }}
    )


@dataclass_json
@dataclass
class PascalCasePerson:
    given_name: str = field(
        metadata={'dataclasses_json': {
            'letter_case': LetterCase.PASCAL
        }}
    )


@dataclass_json
@dataclass
class FieldNamePerson:
    given_name: str = field(metadata=config(field_name='givenName'))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CamelCasePersonWithOverride:
    given_name: str
    years_on_earth: str = field(metadata=config(field_name='age'))


class TestLetterCase:
    def test_camel_encode(self):
        assert CamelCasePerson('Alice').to_json() == '{"givenName": "Alice"}'

    def test_camel_decode(self):
        assert CamelCasePerson.from_json(
            '{"givenName": "Alice"}') == CamelCasePerson('Alice')

    def test_kebab_encode(self):
        assert KebabCasePerson('Alice').to_json() == '{"given-name": "Alice"}'

    def test_kebab_decode(self):
        assert KebabCasePerson.from_json(
            '{"given-name": "Alice"}') == KebabCasePerson('Alice')

    def test_snake_encode(self):
        assert SnakeCasePerson('Alice').to_json() == '{"given_name": "Alice"}'

    def test_snake_decode(self):
        assert SnakeCasePerson.from_json(
            '{"given_name": "Alice"}') == SnakeCasePerson('Alice')

    def test_pascal_encode(self):
        assert PascalCasePerson('Alice').to_json() == '{"GivenName": "Alice"}'

    def test_pascal_decode(self):
        assert PascalCasePerson.from_json(
            '{"GivenName": "Alice"}') == PascalCasePerson('Alice')

    def test_field_name_encode(self):
        assert FieldNamePerson('Alice').to_json() == '{"givenName": "Alice"}'

    def test_field_name_decode(self):
        assert FieldNamePerson.from_json(
            '{"givenName": "Alice"}') == FieldNamePerson('Alice')

    def test_camel_with_override_encode(self):
        assert CamelCasePersonWithOverride(
            'Alice', 10).to_json() == '{"givenName": "Alice", "age": 10}'

    def test_camel_with_override_decode(self):
        expected = CamelCasePersonWithOverride('Alice', 10)
        assert CamelCasePersonWithOverride.from_json(
            '{"givenName": "Alice", "age": 10}') == expected

    def test_from_dict(self):
        assert CamelCasePerson.from_dict(
            {'givenName': 'Alice'}) == CamelCasePerson('Alice')

    def test_to_dict(self):
        assert {'givenName': 'Alice'} == CamelCasePerson('Alice').to_dict()
