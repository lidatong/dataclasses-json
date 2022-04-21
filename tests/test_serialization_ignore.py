from .test_letter_case import FieldNamePerson

expected_ignore_json='{"given_name": "Alice"}'
expected_json='{"givenName": "Alice"}'
expected_ignore_dict={"given_name": "Alice"}
expected_dict={"givenName": "Alice"}

class TestSerializationIgnore:

    def test_to_json_ignore_custom_naming(self):
        assert expected_ignore_json == FieldNamePerson("Alice").to_json(ignore_custom_naming=True)

    def test_to_json_include_custom_naming(self):
        assert expected_json == FieldNamePerson("Alice").to_json(ignore_custom_naming=False)

    def test_to_json_ignore_custom_naming_option(self):
        assert expected_json == FieldNamePerson("Alice").to_json()

    def test_to_dict_ignore_custom_naming(self):
        assert expected_ignore_dict == FieldNamePerson("Alice").to_dict(ignore_custom_naming=True)

    def test_to_dict_include_custom_naming(self):
        assert expected_dict == FieldNamePerson("Alice").to_dict(ignore_custom_naming=False)

    def test_to_dict_ignore_custom_naming_option(self):
        assert expected_dict == FieldNamePerson("Alice").to_dict()

    def test_dump_one_ignore_custom_naming(self):
        person = FieldNamePerson('Alice')
        dump = FieldNamePerson.schema().dump(person, many=False, ignore_custom_naming=True)
        assert expected_ignore_dict == dump

    def test_dump_one_include_custom_naming(self):
        person = FieldNamePerson('Alice')
        dump = FieldNamePerson.schema().dump(person, many=False, ignore_custom_naming=False)
        assert expected_dict == dump

    def test_dump_one_ignore_custom_naming_option(self):
        person = FieldNamePerson('Alice')
        dump = FieldNamePerson.schema().dump(person, many=False)
        assert expected_dict == dump

    def test_dumps_one_ignore_custom_naming(self):
        person = FieldNamePerson('Alice')
        dump = FieldNamePerson.schema().dumps(person, many=False, ignore_custom_naming=True)
        assert expected_ignore_json == dump

    def test_dumps_one_include_custom_naming(self):
        person = FieldNamePerson('Alice')
        dump = FieldNamePerson.schema().dumps(person, many=False, ignore_custom_naming=False)
        assert expected_json == dump

    def test_dumps_one_ignore_custom_naming_option(self):
        person = FieldNamePerson('Alice')
        dump = FieldNamePerson.schema().dumps(person, many=False)
        assert expected_json == dump

    def test_dump_many_ignore_custom_naming(self):
        p1 = FieldNamePerson('Alice')
        p2 = FieldNamePerson('Alex')
        dump = FieldNamePerson.schema().dump([p1,p2], many=True, ignore_custom_naming=True)
        p1_dict = p1.to_dict(ignore_custom_naming=True)
        p2_dict = p2.to_dict(ignore_custom_naming=True)
        assert len(dump) == 2
        assert p1_dict in dump
        assert p2_dict in dump

    def test_dump_many_include_custom_naming(self):
        p1 = FieldNamePerson('Alice')
        p2 = FieldNamePerson('Alex')
        dump = FieldNamePerson.schema().dump([p1,p2], many=True, ignore_custom_naming=False)
        p1_dict = p1.to_dict(ignore_custom_naming=False)
        p2_dict = p2.to_dict(ignore_custom_naming=False)
        assert len(dump) == 2
        assert p1_dict in dump
        assert p2_dict in dump

    def test_dump_many_ignore_custom_naming_option(self):
        p1 = FieldNamePerson('Alice')
        p2 = FieldNamePerson('Alex')
        dump = FieldNamePerson.schema().dump([p1,p2], many=True)
        p1_dict = p1.to_dict()
        p2_dict = p2.to_dict()
        assert len(dump) == 2
        assert p1_dict in dump
        assert p2_dict in dump

    def test_dumps_many_ignore_custom_naming(self):
        p1 = FieldNamePerson('Alice')
        p2 = FieldNamePerson('Alex')
        dump = FieldNamePerson.schema().dumps([p1,p2], many=True, ignore_custom_naming=True)
        p1_json = p1.to_json(ignore_custom_naming=True)
        p2_json = p2.to_json(ignore_custom_naming=True)
        assert p1_json in dump
        assert p2_json in dump

    def test_dumps_many_include_custom_naming(self):
        p1 = FieldNamePerson('Alice')
        p2 = FieldNamePerson('Alex')
        dump = FieldNamePerson.schema().dumps([p1,p2], many=True, ignore_custom_naming=False)
        p1_json = p1.to_json(ignore_custom_naming=False)
        p2_json = p2.to_json(ignore_custom_naming=False)
        assert p1_json in dump
        assert p2_json in dump

    def test_dumps_many_ignore_custom_naming_option(self):
        p1 = FieldNamePerson('Alice')
        p2 = FieldNamePerson('Alex')
        dump = FieldNamePerson.schema().dumps([p1,p2], many=True)
        p1_json = p1.to_json()
        p2_json = p2.to_json()
        assert p1_json in dump
        assert p2_json in dump