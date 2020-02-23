import pytest
# noinspection PyProtectedMember
from dataclasses_json.core import _get_type_hints_cache, _is_supported_generic_cache, _user_overrides_cache


@pytest.fixture(autouse=True)
def clear_caches():
    _is_supported_generic_cache.clear()
    _user_overrides_cache.clear()
    _get_type_hints_cache.clear()
