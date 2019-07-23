from dataclasses import dataclass, field
from enum import Enum

from dataclasses_json import dataclass_json
from marshmallow import fields


class Sex(Enum):
    female = 0
    male = 1


class SexField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return value.name if value is not None else Sex.female

    def _deserialize(self, value, attr, data, **kwargs):
        return Sex[value]


sex_field = {"dataclasses_json": {"mm_field": SexField()}}


@dataclass_json
@dataclass
class Actor:
    sex: Sex = field(default=None, metadata=sex_field)


def run():
    # actor = Actor(sex=Sex.female)
    actor = Actor()
    print()
    print(actor)
    dikt = Actor.schema().dump(actor)
    print(dikt)
    obj = Actor.schema().load(dikt)


if __name__ == "__main__":
    run()
