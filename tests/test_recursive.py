from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin


@dataclass(frozen=True)
class Tree(DataClassJsonMixin):
    value: str
    left: Optional['Tree']
    right: Optional['Tree']


family_tree_json = """
{
    "value": "Boy",
    "left": {
        "value": "Ma",
        "left": {
            "value": "Maternal Grandma",
            "left": null,
            "right": null
        },
        "right": {
            "value": "Maternal Grandpa",
            "left": null,
            "right": null
        }
    },
    "right": {
        "value": "Pa",
        "left": {
            "value": "Paternal Grandma",
            "left": null,
            "right": null
        },
        "right": {
            "value": "Paternal Grandpa",
            "left": null,
            "right": null
        }
    }
}
""".strip()

family_tree = Tree(
    "Boy",
    Tree(
        "Ma",
        Tree(
            "Maternal Grandma",
            None,
            None
        ),
        Tree(
            "Maternal Grandpa",
            None,
            None
        )
    ),
    Tree("Pa",
         Tree(
             "Paternal Grandma",
             None,
             None
         ),
         Tree(
             "Paternal Grandpa",
             None,
             None
         )
         )
)


class TestRecursive:
    def test_tree_encode(self):
        assert family_tree.to_json(indent=4) == family_tree_json

    def test_tree_decode(self):
        assert Tree.from_json(family_tree_json) == family_tree

    def test_tree_schema_round_trip(self):
        tree_dict = Tree.schema().dump(family_tree)
        tree_obj = Tree.schema().load(tree_dict)
        assert tree_obj == family_tree

