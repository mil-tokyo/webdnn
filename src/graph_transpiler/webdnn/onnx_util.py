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
    onnx.TensorProto.FLOAT: np.float32, # 1
    onnx.TensorProto.UINT8: np.uint8, # 2
    onnx.TensorProto.INT8: np.int8, # 3
    onnx.TensorProto.UINT16: np.uint16, # 4
    onnx.TensorProto.INT16: np.int16, # 5
    onnx.TensorProto.INT32: np.int32, # 6
    onnx.TensorProto.INT64: np.int64, # 7
    onnx.TensorProto.BOOL: np.bool, # 9
    onnx.TensorProto.FLOAT16: np.float16, # 10
    onnx.TensorProto.DOUBLE: np.float64, # 11
    onnx.TensorProto.UINT32: np.uint32, # 12
    onnx.TensorProto.UINT64: np.uint64, # 13
}

def tensor_proto_to_numpy(tensor_proto: onnx.TensorProto) -> np.ndarray:
    shape = tuple(tensor_proto.dims)
    dtype = DATA_TYPE_TO_NUMPY[tensor_proto.data_type]
    if tensor_proto.raw_data:
        array = np.frombuffer(tensor_proto.raw_data, dtype=dtype)
    elif tensor_proto.int64_data:
        array = np.array(tensor_proto.int64_data, dtype=dtype)
    elif tensor_proto.int32_data:
        array = np.array(tensor_proto.int32_data, dtype=dtype)
    elif tensor_proto.uint64_data:
        array = np.array(tensor_proto.uint64_data, dtype=dtype)
    elif tensor_proto.float_data:
        array = np.array(tensor_proto.float_data, dtype=dtype)
    elif tensor_proto.double_data:
        array = np.array(tensor_proto.double_data, dtype=dtype)
    array = array.reshape(shape)

    if dtype == np.int64:
        array = np.clip(array, -2**31, 2**31-1).astype(np.int32)
    elif dtype == np.uint64:
        array = np.clip(array, 0, 2**32-1).astype(np.uint32)
    return array
