from dataclasses import dataclass
from typing import List, Tuple, Any

from dataclasses_json import DataClassJsonMixin, dataclass_json
from dataclasses_json.core import _hash_key


def test_hash_key_dataclass():

    @dataclass()
    class DataclassWithMixin(DataClassJsonMixin):
        a: str

    assert _hash_key(DataclassWithMixin) == DataclassWithMixin._dataclass_hash

    @dataclass_json()
    @dataclass()
    class DataClassWithoutMixin:
        b: str

    assert _hash_key(DataClassWithoutMixin) == DataClassWithoutMixin._dataclass_hash


def test_hash_key_type():

    assert _hash_key(List[str]) == repr(List[str])
    assert _hash_key(List) == repr(List)
    assert _hash_key(List) != _hash_key(List[str])
    assert _hash_key(List[Any]) != _hash_key(List[str])

    assert _hash_key(Tuple) == repr(Tuple)
    assert _hash_key(Tuple[int, int]) == repr(Tuple[int, int])
    assert _hash_key(Tuple) != repr(Tuple[int, int])
    assert _hash_key(Tuple[int, str]) != repr(Tuple[int, int])

    assert _hash_key(str) != _hash_key(int)


def test_hash_key_classes():
    class A:
        A: str

    hashkey_original_a = _hash_key(A)

    class B:
        b: str

    assert _hash_key(A) != _hash_key(B)

    class A:
        redefined: str

    # this is the only possible behavior. We do not care about has conflicts here as non-json-encodable so nothing will be cached anyways.
    assert _hash_key(A) == hashkey_original_a

