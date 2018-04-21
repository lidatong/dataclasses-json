# Dataclasses JSON

This library provides a simple API for encoding and decoding [dataclasses](https://www.python.org/dev/peps/pep-0557/) to and from JSON.

It's recursive, so you can easily work with nested dataclasses.

## Quickstart

`pip install dataclasses_json`

```python
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass(frozen=True)
class Minion(DataClassJsonMixin):
    name: str


@dataclass(frozen=True)
class Boss(DataClassJsonMixin):
    minion: Minion


boss = Boss(Minion('evilminion'))
boss_json = """
{
    "minion": {
        "name": "evilminion"
    }
}
""".strip()
assert boss.to_json(indent=4) == boss_json
assert Boss.from_json(boss_json) == boss
```

