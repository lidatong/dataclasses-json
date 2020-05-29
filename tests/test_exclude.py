from dataclasses import dataclass, field

from dataclasses_json.api import DataClassJsonMixin, config
from dataclasses_json.cfg import Exclude


@dataclass
class EncodeExclude(DataClassJsonMixin):
    public_field: str
    private_field: str = field(metadata=config(exclude=Exclude.ALWAYS))


@dataclass
class EncodeInclude(DataClassJsonMixin):
    public_field: str
    private_field: str = field(metadata=config(exclude=Exclude.NEVER))


@dataclass
class EncodeCustom(DataClassJsonMixin):
    public_field: str
    sensitive_field: str = field(
        metadata=config(exclude=lambda v: v.startswith("secret"))
    )


def test_exclude():
    dclass = EncodeExclude(public_field="public", private_field="private")
    encoded = dclass.to_dict()
    assert "public_field" in encoded
    assert "private_field" not in encoded


def test_include():
    dclass = EncodeInclude(public_field="public", private_field="private")
    encoded = dclass.to_dict()
    assert "public_field" in encoded
    assert "private_field" in encoded
    assert encoded["private_field"] == "private"


def test_custom_action_included():
    dclass = EncodeCustom(public_field="public", sensitive_field="notsecret")
    encoded = dclass.to_dict()
    assert "sensitive_field" in encoded


def test_custom_action_excluded():
    dclass = EncodeCustom(public_field="public", sensitive_field="secret")
    encoded = dclass.to_dict()
    assert "sensitive_field" not in encoded
