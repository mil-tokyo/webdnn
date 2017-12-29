import tempfile
from os import path

import numpy as np
from nose.tools import raises
from parameterized import parameterized

from webdnn.util import json
from webdnn.util.json import CustomJSONEncoder, SerializableMixin


def test_serializable_mixin_implemented():
    class Foo(SerializableMixin):
        def __init__(self, name):
            self.name = name

        def _to_serializable_(self):
            return {"name": self.name}

    foo = Foo("hoge")

    res = json.dumps(foo)
    assert res == "{\"name\": \"hoge\"}", res


@raises(NotImplementedError)
def test_serializable_mixin_not_implemented():
    class Foo(SerializableMixin):
        def __init__(self, name):
            self.name = name

    foo = Foo("hoge")
    json.dumps(foo)


@parameterized([
    (np.int8, int), (np.int16, int), (np.int32, int), (np.int64, int), (np.int, int),
    (np.uint8, int), (np.uint16, int), (np.uint32, int), (np.uint64, int), (np.uint, int),
    (np.float16, float), (np.float32, float), (np.float64, float), (np.float, float)
])
def test_custom_encoder_with_numpy_scalar(original_class, expected_class):
    original_data = original_class(0)
    serializable_data = CustomJSONEncoder().default(original_data)
    assert type(serializable_data) == expected_class, type(serializable_data)


@parameterized([
    (np.int8, int), (np.int16, int), (np.int32, int), (np.int64, int), (np.int, int),
    (np.uint8, int), (np.uint16, int), (np.uint32, int), (np.uint64, int), (np.uint, int),
    (np.float16, float), (np.float32, float), (np.float64, float), (np.float, float)
])
def test_custom_encoder_with_numpy_array(original_class, expected_class):
    original_data = np.array([0], dtype=original_class)
    serializable_data = CustomJSONEncoder().default(original_data)
    assert isinstance(serializable_data, list), type(serializable_data)
    assert type(serializable_data[0]) == expected_class, type(serializable_data[0])


@raises(TypeError)
def test_custom_encoder_unsupported_type():
    class Foo:
        pass

    CustomJSONEncoder().default(Foo())


def test_dump_with_native_object():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = path.join(tmpdir, "tmp.json")

        with open(filepath, "w") as f:
            json.dump([1, True, None], f)

        with open(filepath) as f:
            res = f.read()

        assert res == "[1, true, null]", res


def test_dumps():
    res = json.dumps([1, True, None])
    assert res == "[1, true, null]", res
