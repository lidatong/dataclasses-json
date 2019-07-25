from dataclasses import dataclass, field

from marshmallow import fields

from dataclasses_json import dataclass_json


class SchemaRecursionLimitError(Exception):
    def __init__(self):
        super().__init__(
            "Schema recursion limit exceeded.  Generate the schema with a deeper limit or dump with a deeper limit."
        )


class SchemaRecursionLimitField(fields.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._CHECK_ATTRIBUTE = False

    def _serialize(self, value, attr, obj, **kwargs):
        raise SchemaRecursionLimitError()

    def _deserialize(self, value, attr, data, **kwargs):
        raise SchemaRecursionLimitError()


@dataclass_json
@dataclass
class SchemaRecursionLimit:
    dummy_field: str = field(
        default="anything", metadata={"dataclasses_json": {"mm_field": SchemaRecursionLimitField()}}
    )


SCHEMA_RECURSION_LIMIT_SCHEMA = SchemaRecursionLimit.schema()
