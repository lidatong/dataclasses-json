"""
 PEP 0673 that allows self-references has only been added in 3.11
 This suite verifies that we are somewhat able to serde self-referencing classes before 3.11.
"""
import json
from typing import Dict

import pytest

from tests.entities import DataClassWithSelf


class TestSelf:
    @pytest.mark.parametrize("entity, expected", [
        (DataClassWithSelf(id="1", ref=None), {
            "id": "1",
            "ref": None
        }),
        (DataClassWithSelf(id="1", ref=DataClassWithSelf(id="2", ref=None)), {
            "id": "1",
            "ref": { "id": "2", "ref": None }
        })
    ])
    def test_self_serde(self, entity: DataClassWithSelf, expected: Dict):
        assert entity.to_dict() == expected and DataClassWithSelf.from_dict(expected).to_json() == entity.to_json()

    @pytest.mark.parametrize("entity", [
        ({
            "id": "1",
            "ref": {"id": "2", "ref": None}
        }),
        ({
            "id": "1",
            "ref": None
        })
    ])
    def test_self_type(self, entity: Dict):
        obj = DataClassWithSelf.from_json(json.dumps(entity))
        assert isinstance(obj, DataClassWithSelf) and (isinstance(obj.ref, DataClassWithSelf) or isinstance(obj.ref, type(None)))
