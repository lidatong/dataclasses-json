import json
from dataclasses import dataclass, fields as dc_fields
from typing import Any, Optional

import pytest

from dataclasses_json.api import SchemaRecursionLimit, dataclass_json
from dataclasses_json.mm import SchemaRecursionLimitError, RecursionMgr


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

print("Node")
for field in dc_fields(Node):
    print("\t", field)

tree = Node(name="root", left=Node(name="left-1", left=Node(name="left-1-1")))


def test_recursion_under_limit():
    print()
    schema = Node.schema(recursion_mgr=RecursionMgr(3))
    d_rep = schema.dump(tree)
    print("\n", json.dumps(d_rep, indent=2))
    obj = schema.load(d_rep)
    s_rep = schema.dumps(tree, indent=2)
    print("\n", schema.dumps(tree, indent=2))
    obj = schema.loads(s_rep)


def test_recursion_over_limit():
    schema = Node.schema(recursion_mgr=RecursionMgr(1))
    with pytest.raises(SchemaRecursionLimitError):
        schema.dump(tree)
