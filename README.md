# Dataclasses JSON

This library provides a simple API for encoding and decoding [dataclasses](https://www.python.org/dev/peps/pep-0557/) to and from JSON.

It's recursive (see caveats below), so you can easily work with nested dataclasses.

In addition to the supported types in the [py to JSON table](https://docs.python.org/3/library/json.html#py-to-json-table), any arbitrary
[Collection](https://docs.python.org/3/library/collections.abc.html#collections.abc.Collection) type is supported (they are encoded into JSON arrays, but decoded into the original collection types).

**The [latest release](https://github.com/lidatong/dataclasses-json/releases/latest) is compatible with both Python 3.7 and Python 3.6 (with the dataclasses backport).** 

## Quickstart
`pip install dataclasses-json`

```python
my_dataclass_instance.to_json()
MyDataClass.from_json(some_json_string)
```

```python
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass(frozen=True)
class Minion():
    name: str


@dataclass(frozen=True)
class Boss(DataClassJsonMixin):
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
Data Classes that contain forward references (e.g. recursive dataclasses) are not currently supported.
