# Dataclasses JSON

This library provides a simple API for encoding and decoding [dataclasses](https://docs.python.org/3/library/dataclasses.html) to and from JSON.

It's recursive (see caveats below), so you can easily work with nested dataclasses.
In addition to the supported types in the [py to JSON table](https://docs.python.org/3/library/json.html#py-to-json-table), any arbitrary
[Collection](https://docs.python.org/3/library/collections.abc.html#collections.abc.Collection) type is supported (they are encoded into JSON arrays, but decoded into the original collection types).

**The [latest release](https://github.com/lidatong/dataclasses-json/releases/latest) is compatible with both Python 3.7 and Python 3.6 (with the dataclasses backport).**

## Quickstart
`pip install dataclasses-json`

#### Approach 1: Class decorator

```python
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Person:
    name: str

lidatong = Person('lidatong')

# Encoding to JSON
lidatong.to_json()  # '{"name": "lidatong"}'

# Decoding from JSON
Person.from_json('{"name": "lidatong"}')  # Person(name='lidatong')
```

Note that the `@dataclass_json` decorator must be stacked above the `@dataclass`
decorator (order matters!)

#### Approach 2: Inherit from a mixin

```python
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

@dataclass
class Person(DataClassJsonMixin):
    name: str

lidatong = Person('lidatong')

# A different example from Approach 1 above, but usage is the exact same
assert Person.from_json(lidatong.to_json()) == lidatong
```

Pick whichever approach suits your taste. The differences in implementation are
invisible in usage.

## How do I...

### Encode or decode a JSON array containing instances of my Data Class?

```python
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Person:
    name: str
```

**Encode**

```python
people_json = [Person('lidatong')]
Person.schema().dumps(people_json, many=True)  # '[{"name": "lidatong"}]'
```

**Decode**

```python
people_json = '[{"name": "lidatong"}]'
Person.schema().loads(people_json, many=True)  # [Person(name='lidatong')]
```

### Encode or decode into Python lists/dictionaries rather than JSON?

This can be by calling `.schema()` and then using the corresponding 
encoder/decoder methods, ie. `.load(...)`/`.dump(...)`.

**Encode into a single Python dictionary**

```python
person = Person('lidatong')
Person.schema().dump(person)  # {"name": "lidatong"}
```

**Encode into a list of Python dictionaries**

```python
people = [Person('lidatong')]
Person.schema().dump(people, many=True)  # [{"name": "lidatong"}]
```

**Decode a dictionary into a single dataclass instance**

```python
person_dict = {"name": "lidatong"}
Person.schema().load(person_dict)  # Person(name='lidatong')
```

**Decode a list of dictionaries into a list of dataclass instances**

```python
people_dicts = [{"name": "lidatong"}]
Person.schema().load(people_dicts, many=True)  # [Person(name='lidatong')]
```

### Explanation

Briefly, on what's going on under the hood in the above examples: calling 
`.schema()` will have this library generate a
[marshmallow schema]('https://marshmallow.readthedocs.io/en/3.0/api_reference.html#schema)
for you. It also fills in the corresponding object hook, so that marshmallow
will create an instance of your Data Class on `load` (e.g.
`Person.schema().load` returns a `Person`) rather than a `dict`, which it does
by default in marshmallow.


## Marshmallow interop

Using the `dataclass_json` decorator or mixing in `DataClassJsonMixin` will
provide you with an additional method `.schema()`.

`.schema()` generates a schema exactly equivalent to manually creating a
marshmallow schema for your dataclass. You can reference the [marshmallow API docs](https://marshmallow.readthedocs.io/en/3.0/api_reference.html#schema)
to learn other ways you can use the schema returned by `.schema()`.

You can pass in the exact same arguments to `.schema()` that you would when
constructing a `PersonSchema` instance, e.g. `.schema(many=True)`, and they will
get passed through to the marshmallow schema.

```python
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Person:
    name: str

# You don't need to do this - it's generated for you by `.schema()`!
from marshmallow import Schema, fields

class PersonSchema(Schema):
    name = fields.Str()
```

## A larger example

```python
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List

@dataclass_json
@dataclass(frozen=True)
class Minion:
    name: str


@dataclass_json
@dataclass(frozen=True)
class Boss:
    minions: List[Minion]

boss = Boss([Minion('evil minion'), Minion('very evil minion')])
boss_json = """
{
    "minions": [
        {
            "name": "evil minion"
        },
        {
            "name": "very evil minion"
        }
    ]
}
""".strip()

assert boss.to_json(indent=4) == boss_json
assert Boss.from_json(boss_json) == boss
```


## Caveats
Data Classes that contain forward references (e.g. recursive dataclasses) are
not currently supported.

