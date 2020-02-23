from tests.entities import (DataClassWithDataClass,
                            DataClassWithList,
                            DataClassX,
                            DataClassXs)
# noinspection PyProtectedMember
from dataclasses_json.core import _get_type_hints_cache, _is_supported_generic_cache, _user_overrides_cache


class TestCache:

    def test_dataclass_with_xs_caches_class(self):
        json_dataclass_with_xs = '{"xs": [{"x": 1}]}'
        _ = DataClassXs.from_json(json_dataclass_with_xs)

        # type hints for class and DataClassX cached
        assert _get_type_hints_cache._Cache__currsize == 2
        # supported generic called for List[DataClassX] and int
        assert _is_supported_generic_cache._Cache__currsize == 2
        # for the dataclasses
        assert _user_overrides_cache._Cache__currsize == 2

        # force cache hits
        _ = DataClassXs.from_json(json_dataclass_with_xs)

        assert _get_type_hints_cache._Cache__currsize == 2
        assert _is_supported_generic_cache._Cache__currsize == 2
        assert _user_overrides_cache._Cache__currsize == 2

    def test_dataclass_with_x_caches_class(self):
        json_dataclass_with_x = '{"x": 1}'
        _ = DataClassX.from_json(json_dataclass_with_x)

        # type hints for class cached
        assert _get_type_hints_cache._Cache__currsize == 1
        # supported generic called for int
        assert _is_supported_generic_cache._Cache__currsize == 1
        # for the dataclass
        assert _user_overrides_cache._Cache__currsize == 1

        # force cache hits
        _ = DataClassX.from_json(json_dataclass_with_x)

        assert _get_type_hints_cache._Cache__currsize == 1
        assert _is_supported_generic_cache._Cache__currsize == 1
        assert _user_overrides_cache._Cache__currsize == 1

    def test_dataclass_with_list_caches_class(self):
        json_dataclass_with_list = '{"xs": [1]}'
        _ = DataClassWithList.from_json(json_dataclass_with_list)

        # type hints for class cached
        assert _get_type_hints_cache._Cache__currsize == 1
        # supported generic called for List[int] and int itself
        assert _is_supported_generic_cache._Cache__currsize == 2
        # for the dataclass
        assert _user_overrides_cache._Cache__currsize == 1

        # force cache hits
        _ = DataClassWithList.from_json(json_dataclass_with_list)

        assert _get_type_hints_cache._Cache__currsize == 1
        assert _is_supported_generic_cache._Cache__currsize == 2
        assert _user_overrides_cache._Cache__currsize == 1

    def test_nested_dataclass_caches_both_classes(self):
        json_dataclass_with_dataclass = '{"dc_with_list": {"xs": [1]}}'
        _ = DataClassWithDataClass.from_json(json_dataclass_with_dataclass)

        assert _get_type_hints_cache._Cache__currsize == 2
        # supported generic called for List[int] and int
        assert _is_supported_generic_cache._Cache__currsize == 2
        # for the dataclasses
        assert _user_overrides_cache._Cache__currsize == 2

        # force cache_hit
        _ = DataClassWithDataClass.from_json(json_dataclass_with_dataclass)

        assert _get_type_hints_cache._Cache__currsize == 2
        assert _is_supported_generic_cache._Cache__currsize == 2
        assert _user_overrides_cache._Cache__currsize == 2
