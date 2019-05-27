from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

@dataclass_json(parse_as_subtype=True)
@dataclass(frozen=True)
class Base:
    x: int


@dataclass_json(register_subtype_of=Base)
@dataclass(frozen=True)
class SubclassFoo(Base):
    y: str


@dataclass_json(register_subtype_of=Base, subtype_id='bar')
@dataclass(frozen=True)
class SubclassBar(Base):
    z: int


@dataclass_json
@dataclass(frozen=True)
class BaseContainer:
    id: int
    children: List[Base]


@dataclass_json(parse_as_subtype=True, subtype_property='@id')
@dataclass(frozen=True)
class BaseWCustomProperty:
    x: int


@dataclass_json(register_subtype_of=BaseWCustomProperty, subtype_id='sub')
@dataclass(frozen=True)
class CustomPropertySub(BaseWCustomProperty):
    y: str


b = Base(1)
foo = SubclassFoo(2, 'abc')
bar = SubclassBar(3, 45)

c = BaseContainer(999, [b, foo, bar])

class TestSubclasses:
    def test_custom_proprety(self):
        bb = BaseWCustomProperty(22)
        sub = CustomPropertySub(33, 'j')

        assert bb.to_json() == '{"x": 22}'
        assert sub.to_json() == '{"x": 33, "y": "j", "@id": "sub"}'

        psub = BaseWCustomProperty.from_json(
            '{"x": 33, "y": "j", "@id": "sub"}')

        assert psub == sub

    def test_badsubclass(self):
        class X:
            pass

        try:
          @dataclass_json(register_subtype_of=X)
          @dataclass(frozen=True)
          class BadSubclass(X):
              z: int

        except ValueError as e:
            assert 'parse_as_subtype' in e.args[0], e
        
    def test_base(self):
        assert b.to_json() == '{"x": 1}'

    def test_foo(self):
        assert foo.to_json() == '{"x": 2, "y": "abc", "@type": "SubclassFoo"}'

    def test_bar(self):
        assert bar.to_json() == '{"x": 3, "z": 45, "@type": "bar"}'

    def test_container(self):
        assert c.to_json() == \
            '{"id": 999, "children": [' \
            '{"x": 1}, ' \
            '{"x": 2, "y": "abc", "@type": "SubclassFoo"}, ' \
            '{"x": 3, "z": 45, "@type": "bar"}]}'

    def test_parse(self):
        pc = BaseContainer.from_json(c.to_json())

        assert pc == c
