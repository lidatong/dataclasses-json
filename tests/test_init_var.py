from dataclasses import InitVar, dataclass
from typing import Optional

import pytest

from dataclasses_json import DataClassJsonMixin


@dataclass
class A(DataClassJsonMixin):
    a_init: InitVar[int]
    _a: Optional[int] = None

    def __post_init__(self, a_init: int):
        self._a = a_init


class TestEncoder:
    def test_init_var(self):
        assert A(a_init=1).to_dict() == {'_a': 1}


class TestDecoder:
    def test_init_var(self):
        result = A.from_dict({'a_init': 1})
        assert result._a == 1
