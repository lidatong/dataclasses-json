from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, DataClassJsonMixin


def test_multiple_classes_same_name():

    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass(frozen=True)
    class Camel(DataClassJsonMixin):
        test_field: float

    @dataclass_json(letter_case=LetterCase.SNAKE)
    @dataclass(frozen=True)
    class Snake(DataClassJsonMixin):
        test_field: float


    camel1 = Camel(test_field=5)
    snake1 = Snake(test_field=10)

    assert camel1.to_dict()['testField'] == camel1.test_field
    assert snake1.to_dict()['test_field'] == snake1.test_field

    # redefine classes with the same name to replace current object at id(Camel)
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass(frozen=True)
    class Camel(DataClassJsonMixin):
        test_field: float


    @dataclass_json(letter_case=LetterCase.SNAKE)
    @dataclass(frozen=True)
    class Snake(DataClassJsonMixin):
        test_field: float

    camel1 = Camel(test_field=5)
    snake1 = Snake(test_field=10)
    print('camel', camel1.to_json())
    print('snake', snake1.to_json())

    assert camel1.to_dict()['testField'] == camel1.test_field
    assert snake1.to_dict()['test_field'] == snake1.test_field
