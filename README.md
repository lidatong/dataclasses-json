# Dataclasses JSON

This library provides a simple API for encoding and decoding [dataclasses](https://docs.python.org/3/library/dataclasses.html) to and from JSON.

It's very quick to get started. Here's a quick example:

```python
# after running `pip install dataclasses-json`

from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class SimpleExample:
    int_field: int

simple_example = SimpleExample(1)

# Encoding to JSON. Note the output is a string, not a dictionary.
simple_example.to_json()  # {"int_field": 1}

# Decoding from JSON. Note the input is a string, not a dictionary.
SomeData.from_json('{"int_field": 1}')  # SimpleExample(1)

# Encoding to a (JSON) dict
my_number.to_dict()  # {'int_field': 1}

# Decoding from a (JSON) dict
MyNumber.from_dict({'int_field': 1})  # SimpleExample(1)
```

## Supported types

It's recursive (see caveats below), so you can easily work with nested dataclasses.
In addition to the supported types in the 
[py to JSON table](https://docs.python.org/3/library/json.html#py-to-json-table), this library supports the following:
- any arbitrary [Collection](https://docs.python.org/3/library/collections.abc.html#collections.abc.Collection) type is supported.
[Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) types are encoded as JSON objects and `str` types as JSON strings. 
Any other Collection types are encoded into JSON arrays, but decoded into the original collection types.
- [datetime](https://docs.python.org/3/library/datetime.html#available-types) 
objects. `datetime` objects are encoded to `float` (JSON number) using 
[timestamp](https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp).
As specified in the `datetime` docs, if your `datetime` object is naive, it will 
assume your system local timezone when calling `.timestamp()`. JSON nunbers 
corresponding to a `datetime` field in your dataclass are decoded 
into a datetime-aware object, with `tzinfo` set to your system local timezone.
Thus, if you encode a datetime-naive object, you will decode into a 
datetime-aware object. This is important, because encoding and decoding won't 
strictly be inverses. See this section if you want to override this default
behavior (for example, if you want to use ISO).
- [UUID](https://docs.python.org/3/library/uuid.html#uuid.UUID) objects. They 
are encoded as `str` (JSON string).


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


### Use my dataclass with JSON arrays or objects?

```python
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Person:
    name: str
```

**Encode into a JSON array containing instances of my Data Class**

```python
people_json = [Person('lidatong')]
Person.schema().dumps(people_json, many=True)  # '[{"name": "lidatong"}]'
```

**Decode a JSON array containing instances of my Data Class**

```python
people_json = '[{"name": "lidatong"}]'
Person.schema().loads(people_json, many=True)  # [Person(name='lidatong')]
```

**Encode as part of a larger JSON object containing my Data Class (e.g. an HTTP 
request/response)**

```python
import json

person_dict = Person.schema().dump(Person('lidatong'))

response_dict = {
    'response': {
        'person': person_dict
    }
}

response_json = json.dumps(response_dict)
```

In this case, we do two steps. First, we encode the dataclass into a 
**python dictionary** rather than a JSON string, using `schema()` and `dump`. 
Scroll down for a section addressing that.

Second, we leverage the built-in `json.dumps` to serialize our `dataclass` into 
a JSON string.

**Decode as part of a larger JSON object containing my Data Class (e.g. an HTTP 
response)**

```python
import json

response_dict = json.loads('{"response": {"person": {"name": "lidatong"}}}')

person_dict = response_dict['response']

person = Person.schema().load(person_dict)
```

In a similar vein to encoding above, we leverage the built-in `json` module.

First, call `json.loads` to read the entire JSON object into a 
dictionary. We then access the key of the value containing the encoded dict of 
our `Person` that we want to decode (`response_dict['response']`).

Second, we load in the dictionary using `Person.schema().load`.




### Encode or decode into Python lists/dictionaries rather than JSON?

This can be by calling `.schema()` and then using the corresponding 
encoder/decoder methods, ie. `.load(...)`/`.dump(...)`.

**Encode into a single Python dictionary**

```python
person = Person('lidatong')
person.to_dict()  # {'name': 'lidatong'}
```

**Encode into a list of Python dictionaries**

```python
people = [Person('lidatong')]
Person.schema().dump(people, many=True)  # [{'name': 'lidatong'}]
```

**Decode a dictionary into a single dataclass instance**

```python
person_dict = {'name': 'lidatong'}
Person.from_dict(person_dict)  # Person(name='lidatong')
```

**Decode a list of dictionaries into a list of dataclass instances**

```python
people_dicts = [{"name": "lidatong"}]
Person.schema().load(people_dicts, many=True)  # [Person(name='lidatong')]
```

### Handle missing or optional field values when decoding?

By default, any fields in your dataclass that use `default` or 
`default_factory` will have the values filled with the provided default, if the
corresponding field is missing from the JSON you're decoding.

**Decode JSON with missing field**

```python
@dataclass_json
@dataclass
class Student:
    id: int
    name: str = 'student'

Student.from_json('{"id": 1}')  # Student(id=1, name='student')
```

Notice `from_json` filled the field `name` with the specified default 'student'
when it was missing from the JSON.

Sometimes you have fields that are typed as `Optional`, but you don't 
necessarily want to assign a default. In that case, you can use the 
`infer_missing` kwarg to make `from_json` infer the missing field value as `None`.

**Decode optional field without default**

```python
@dataclass_json
@dataclass
class Tutor:
    id: int
    student: Optional[Student] = None

Tutor.from_json('{"id": 1}')  # Tutor(id=1, student=None)
```

Personally I recommend you leverage dataclass defaults rather than using 
`infer_missing`, but if for some reason you need to decouple the behavior of 
JSON decoding from the field's default value, this will allow you to do so.

### Explanation

Briefly, on what's going on under the hood in the above examples: calling 
`.schema()` will have this library generate a
[marshmallow schema]('https://marshmallow.readthedocs.io/en/3.0/api_reference.html#schema)
for you. It also fills in the corresponding object hook, so that marshmallow
will create an instance of your Data Class on `load` (e.g.
`Person.schema().load` returns a `Person`) rather than a `dict`, which it does
by default in marshmallow.

**Performance note**

`.schema()` is not cached (it generates the schema on every call), so if you
have a nested Data Class you may want to save the result to a variable to 
avoid re-generation of the schema on every usage.

```python
person_schema = Person.schema()
person_schema.dump(people, many=True)

# later in the code...

person_schema.dump(person)
```


### Override the default encode / decode / marshmallow field of a specific field?

See [Overriding](#Overriding)



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

## Overriding / Extending

#### Overriding

For example, you might want to encode/decode `datetime` objects using ISO format
rather than the default `timestamp`.

```python
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from datetime import datetime
from marshmallow import fields

@dataclass_json
@dataclass
class DataClassWithIsoDatetime:
    created_at: datetime = field(
        metadata={'dataclasses_json': {
            'encoder': datetime.isoformat,
            'decoder': datetime.fromisoformat,
            'mm_field': fields.DateTime(format='iso')
        }})
```

#### Extending

Similarly, you might want to extend `dataclasses_json` to encode `date` objects.

```python
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from datetime import date
from marshmallow import fields

@dataclass_json
@dataclass
class DataClassWithIsoDatetime:
    created_at: date = field(
        metadata={'dataclasses_json': {
            'encoder': date.isoformat,
            'decoder': date.fromisoformat,
            'mm_field': fields.DateTime(format='iso')
        }})
```

As you can see, you can **override** or **extend** the default codecs by providing a "hook" via a 
callable:
- `encoder`: a callable, which will be invoked to convert the field value when encoding to JSON
- `decoder`: a callable, which will be invoked to convert the JSON value when decoding from JSON
- `mm_field`: a marshmallow field, which will affect the behavior of any operations involving `.schema()`

Note that these hooks will be invoked regardless if you're using 
`.to_json`/`dump`/`dumps`
and `.from_json`/`load`/`loads`. So apply overrides / extensions judiciously, making sure to 
carefully consider whether the interaction of the encode/decode/mm_field is consistent with what you expect!

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
