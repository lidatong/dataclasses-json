import json
from dataclasses import dataclass, fields as dc_fields
from typing import Any, Optional

import pytest

from dataclasses_json import dataclass_json
from dataclasses_json.recursion import RecursionMgr
from dataclasses_json.recursion_limit import SchemaRecursionLimitError, SchemaRecursionLimit


def test_schema_recursion_limit_error():
    """
    Check that the SchemaRecursionLimitError is raised whenever
    the SchemaRecursionLimit object is serialized or deserialized.
    This should happen when a schema isn't built deep enough to
    support the level of recursion in a object tree.
    """
    with pytest.raises(SchemaRecursionLimitError):
        SchemaRecursionLimit.schema().dumps(SchemaRecursionLimit())

    str_rep = '{"dummy_field": "anything"}'
    with pytest.raises(SchemaRecursionLimitError):
        SchemaRecursionLimit.schema().loads(str_rep)


@dataclass_json
@dataclass
class Node:
    name: str
    left: Any = None
    right: Any = None


Node.__annotations__.update(left=Optional[Node])
Node.__annotations__.update(right=Optional[Node])
Node = dataclass(Node)

tree_obj = Node(name="root", left=Node(name="left", left=Node(name="left-left"), right=Node(name="left-right")))

def test_recursion_schema_under_limit():
    print()
    schema = Node.schema(recursion_mgr=RecursionMgr(3))
    dikt = schema.dump(tree_obj)
    obj = schema.load(dikt)

    assert "left-left" == obj.left.left.name
    assert "left-right" == obj.left.right.name


def test_recursion_schema_over_limit():
    schema = Node.schema(recursion_mgr=RecursionMgr(1))
    with pytest.raises(SchemaRecursionLimitError) as exc:
        schema.dump(tree_obj)


def test_recursion_dict():
    # Make sure that recursion manager doesn't break anything.
    # To and From dict don't use a schema for validation.
    dikt = Node.to_dict(tree_obj)
    obj = Node.from_dict(dikt)

    assert "left-left" == obj.left.left.name
    assert "left-right" == obj.left.right.name


def test_recursion_json():
    # Make sure that recursion manager doesn't break anything.
    # To and From dict don't use a schema for validation.
    json_str = Node.to_dict(tree_obj)
    obj = Node.from_dict(json_str)

    assert "left-left" == obj.left.left.name
    assert "left-right" == obj.left.right.name
