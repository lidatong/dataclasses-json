from dataclasses import dataclass
import pytest
from typing import Optional, Set, List

from dataclasses_json import dataclass_json
import sys


# This test exists *only* to demonstrate a bug on Python 3.9+
# It uses syntax that is not valid on earlier versions of Python!
if sys.version_info >= (3, 9):
    @dataclass_json
    @dataclass
    class Config:
        options: list["Option"]

    @dataclass_json
    @dataclass
    class Option:
        label: str

    @dataclass_json
    @dataclass
    class ConfigWithoutStringOptions:
        options: list[Option]




@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires generic types for bug")
class TestWarning:
    def test_warns_about_nondeterministic_resolution(self):
        with pytest.warns(UserWarning, match="Assuming hint Option resolves to .*"):
            config = Config.from_dict({"options": [{"label": "scope"}]})
        assert config.to_json() == '{"options": [{"label": "scope"}]}'


    @pytest.mark.filterwarnings("error")
    def test_plain_type_hints_resolve_correctly(self):
        ConfigWithoutStringOptions.from_dict({"options": [{"label": "scope"}]})
