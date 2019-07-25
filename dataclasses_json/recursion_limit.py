"""
Errors, Fields and Classes for new terminal nodes when a recursion manager stops
pushing down another level.
"""
from dataclasses import dataclass, field

from marshmallow import fields

from dataclasses_json import dataclass_json


class SchemaRecursionLimitError(Exception):
    """Error raised when the recursion manager as at the maximum depth."""
    def __init__(self):
        super().__init__(
            "Schema recursion limit exceeded.  Generate the schema with a deeper limit or dump with a deeper limit."
        )


class SchemaRecursionLimitField(fields.Field):
    """
    Special field to raise exception if a object is being serialized or deserialized and the maximum
    depth of the built schema has been reached.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep fields.Field.serialize from adding a default value and not calling the _serialize, _deserialize method.
        self._CHECK_ATTRIBUTE = False

    def _serialize(self, value, attr, obj, **kwargs):
        raise SchemaRecursionLimitError()

    def _deserialize(self, value, attr, data, **kwargs):
        raise SchemaRecursionLimitError()


@dataclass_json
@dataclass
class SchemaRecursionLimit:
    """
    Class to generate a schema for that will raise SchemaRecursionLimitError if it is serialized or deserialized.
    """
    dummy_field: str = field(
        default="anything", metadata={"dataclasses_json": {"mm_field": SchemaRecursionLimitField()}}
    )

# Single copy of the schema for the terminal node in a recursive schema.
SCHEMA_RECURSION_LIMIT_SCHEMA = SchemaRecursionLimit.schema()
