import warnings
from dataclasses import dataclass, field
from typing import List, Optional

import pytest

from dataclasses_json import config, dataclass_json


@pytest.mark.parametrize("field_type", [List[str], Optional[List[str]]])
@pytest.mark.parametrize("method, payload", [
    ("from_dict", {"test_list": None}),
    ("from_json", '{"test_list": null}'),
])
def test_field_decoder_receives_explicit_none(field_type, method, payload):
    calls = []

    def decode(value):
        calls.append(value)
        return [] if value is None else value

    @dataclass_json
    @dataclass
    class Example:
        test_list: field_type = field(
            default_factory=list, metadata=config(decoder=decode)
        )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = getattr(Example, method)(payload)

    assert calls == [None]
    assert result.test_list == []
    assert not [w for w in caught if issubclass(w.category, RuntimeWarning)]
