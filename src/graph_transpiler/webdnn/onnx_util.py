import numpy as np
import onnx


def get_attr_int(op: onnx.NodeProto, name, default=None):
    for attr in op.attribute:
        if attr.name == name:
            return attr.i
    return default


def get_attr_ints(op: onnx.NodeProto, name, default=None):
    for attr in op.attribute:
        if attr.name == name:
            return list(attr.ints)
    return default


def get_attr_float(op: onnx.NodeProto, name, default=None):
    for attr in op.attribute:
        if attr.name == name:
            return attr.f
    return default


DATA_TYPE_TO_NUMPY = {
    1: np.float32,
    2: np.uint8,
    3: np.int8,
    4: np.uint16,
    5: np.int16,
    6: np.int32,
    7: np.int64,
    9: np.bool,
    10: np.float16,
    11: np.float64,
    12: np.uint32,
    13: np.uint64,
}

def tensor_proto_to_numpy(tensor_proto: onnx.TensorProto) -> np.ndarray:
    shape = tuple(tensor_proto.dims)
    dtype = DATA_TYPE_TO_NUMPY[tensor_proto.data_type]
    array = np.frombuffer(tensor_proto.raw_data, dtype=dtype).reshape(shape)
    if dtype == np.int64:
        array = np.clip(array, -2**31, 2**31-1).astype(np.int32)
    elif dtype == np.uint64:
        array = np.clip(array, 0, 2**32-1).astype(np.uint32)
    return array
