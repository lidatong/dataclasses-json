from .entities import (DataClassDefaultListStr, DataClassDefaultOptionalList, DataClassList, DataClassOptional,
                       DataClassWithNestedOptional, DataClassWithNestedOptionalAny, DataClassWithNestedAny)
from .test_letter_case import CamelCasePerson, KebabCasePerson, SnakeCasePerson, FieldNamePerson

test_do_list = """[{}, {"children": [{"name": "a"}, {"name": "b"}]}]"""
test_list = '[{"children": [{"name": "a"}, {"name": "b"}]}]'
nested_optional_data = '{"a": {"test": null}}'


class TestSchema:
    def test_default_list_str(self):
        DataClassDefaultListStr.schema().dumps(DataClassDefaultListStr())
        assert True

    def test_default_optional_list(self):
        DataClassDefaultOptionalList.schema().loads(test_do_list, many=True)
        assert True

    def test_list(self):
        DataClassList.schema().loads(test_list, many=True)
        assert True

    def test_optional(self):
        DataClassOptional.schema().loads('{"a": 4, "b": null}')
        assert True

    def test_letter_case(self):
        for cls in (CamelCasePerson, KebabCasePerson, SnakeCasePerson, FieldNamePerson):
            p = cls('Alice')
            assert p.to_dict() == cls.schema().dump(p)

    def test_nested_optional(self):
        DataClassWithNestedOptional.schema().loads(nested_optional_data)
        assert True

    def test_nested_optional_any(self):
        DataClassWithNestedOptionalAny.schema().loads(nested_optional_data)
        assert True

    def test_nested_any_accepts_optional(self):
        DataClassWithNestedAny.schema().loads(nested_optional_data)
        assert True
