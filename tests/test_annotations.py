import json

# noinspection PyCompatibility
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

from typing import List, Dict, Any
from mypy.main import main as mypy_main

@dataclass
class User(DataClassJsonMixin):
    id: str
    name: str = "John"

class TestAnnotations:
    u: User = User('ax9ssFxH')
    j: str = u.to_json()
    u2: User = User.from_json(j)
    u2a: User = User.from_json(j.encode())

    jMany = [{"id":"115412", "name": "Peter"}, {"id": "atxXxGhg", "name": "Parker"}]
    sch = User.schema()
    users1: List[User] = sch.loads(json.dumps(jMany), many=True)
    n: str = users1[1].name
    users2: List[User] = sch.load(jMany, many=True)
    u3: User = sch.load(jMany[1])
    j2: Dict[str, Any] = sch.dump(u)
    j3: List[Dict[str, Any]] = sch.dump([u2, u3], many=True)
    j4: str = sch.dumps(u2)

    def test_type_hints(self):
        try:
            mypy_main(None, [ __file__  ])
        except SystemExit:
            passed = False
        else:
            passed = True

        # To prevent large errors
        if (not passed):
            raise AssertionError("Type annotations check failed")
