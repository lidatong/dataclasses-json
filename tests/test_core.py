from dataclasses import dataclass
import pytest
from typing import Optional, Set

from dataclasses_json import dataclass_json


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




class TestWarning:
    def test_warns_about_nondeterministic_resolution(self):
        with pytest.warns(UserWarning, match="Assuming hint Option resolves to .*"):
            config = Config.from_dict({"options": [{"label": "scope"}]})
        assert config.to_json() == '{"options": [{"label": "scope"}]}'


    @pytest.mark.filterwarnings("error")
    def test_plain_type_hints_resolve_correctly(self):
        ConfigWithoutStringOptions.from_dict({"options": [{"label": "scope"}]})
