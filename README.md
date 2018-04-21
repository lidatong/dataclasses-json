# Dataclasses JSON

This library provides a simple API for encoding and decoding [dataclasses](https://www.python.org/dev/peps/pep-0557/) to and from JSON.

It's recursive (see caveats below), so you can easily work with nested dataclasses.

In addition to the supported types in the [py to JSON table](https://docs.python.org/3/library/json.html#py-to-json-table), the `set` type
is supported (and more collection types may be included in later releases).


## Quickstart

`pip install dataclasses_json`

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
Generic types and recursive types (types that require forward references)
are not currently supported.
