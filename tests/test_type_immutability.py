from dataclasses import dataclass

import pytest

from dataclasses_json import DataClassJsonMixin


@dataclass
class MyDataclass(DataClassJsonMixin):
    this_must_be_bool: bool
    this_must_be_string: str


def test_type_immutability():
    d = {"this_must_be_bool": 1234, "this_must_be_string": 1234}
    with pytest.raises(Exception) as ser_failure:
        print(MyDataclass.from_dict(d))
