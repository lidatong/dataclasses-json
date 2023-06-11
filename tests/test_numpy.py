from dataclasses import dataclass

from dataclasses_json import dataclass_json
from dataclasses_json.core import np_available

if np_available:
    import numpy as np

    @dataclass_json
    @dataclass(frozen=True)
    class DataWithNumpy:
        int1: np.int64
        float1: np.float64
        array1: np.ndarray
        array2: np.ndarray

    d1 = DataWithNumpy(int1=np.int64(1), float1=np.float64(2.5),
                       array1=np.array([1]), array2=np.array([2.5]))
    d1_json = '{"int1": 1, "float1": 2.5, "array1": [1], "array2": [2.5]}'

    class TestEncoder:
        def test_data_with_numpy(self):
            assert (
                d1.to_json() == d1_json
            ), f"Actual: {d1.to_json()}, Expected: {d1_json}"
