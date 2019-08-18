import copy
from dataclasses import dataclass, field
from typing import Callable, Dict

from dataclasses_json import dataclass_json
from dataclasses_json.callable_alias import  function_alias, aliased_function_field, method_alias, aliased_method_field


@function_alias("hello-world-function")
def greet(data: Dict) -> Dict:
    print(data[FunctionNode.KEY])
    return copy.deepcopy(data)


class Greeter:
    @method_alias("hello-world-method")
    def greet(self, data: Dict) -> Dict:
        print(data[MethodNode.KEY])
        return data


@dataclass_json
@dataclass
class FunctionNode:
    KEY = "msg"
    name: str
    # First argument is list of arguments.  Second argument is the return type.
    callable: Callable[[Dict], Dict] = field(metadata=aliased_function_field)


@dataclass_json
@dataclass
class MethodNode:
    KEY = "msg"
    name: str
    # First argument is list of arguments.  Second argument is the return type.
    callable: Callable[[Dict], Dict] = field(metadata=aliased_method_field)


def _validate_function(capsys, node, node_dict, node_obj):
    assert node_dict["callable"] == "hello-world-function"
    assert node_obj.name == "Hello"
    assert node_obj.callable == greet
    assert node_obj == node
    input = {FunctionNode.KEY: "Hello, World!"}
    result = node_obj.callable(input)
    assert result == input
    out = capsys.readouterr().out
    assert out.strip() == input[FunctionNode.KEY]


def test_aliased_function_dict(capsys):
    node = FunctionNode("Hello", greet)
    node_dict = FunctionNode.to_dict(node)
    node_obj = FunctionNode.from_dict(node_dict)
    _validate_function(capsys, node, node_dict, node_obj)


def test_aliased_function_schema(capsys):
    node = FunctionNode("Hello", greet)
    node_dict = FunctionNode.schema().dump(node)
    node_obj = FunctionNode.schema().load(node_dict)
    _validate_function(capsys, node, node_dict, node_obj)


def _validate_method(capsys, node_dict, node_obj):
    assert node_dict["callable"] == "hello-world-method"
    assert node_obj.name == "Hello"
    input = {FunctionNode.KEY: "Hello, World!"}
    result = node_obj.callable(input)
    assert result == input
    out = capsys.readouterr().out
    assert out.strip() == input[FunctionNode.KEY]


def test_aliased_method_dict(capsys):
    greeter = Greeter()
    node = MethodNode("Hello", greeter.greet)
    node_dict = MethodNode.to_dict(node)
    node_obj = MethodNode.from_dict(node_dict)
    assert node_dict["callable"] == "hello-world-method"
    _validate_method(capsys, node_dict, node_obj)


def test_aliased_method_schema(capsys):
    greeter = Greeter()
    node = MethodNode("Hello", greeter.greet)
    node_dict = MethodNode.schema().dump(node)
    node_obj = MethodNode.schema().load(node_dict)
    assert node_dict["callable"] == "hello-world-method"
    _validate_method(capsys, node_dict, node_obj)
