from dataclasses import dataclass, field

from dataclasses_json import LetterCase, dataclass_json


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
