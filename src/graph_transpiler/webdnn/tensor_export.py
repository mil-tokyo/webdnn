from typing import Dict, List
import struct
import numpy as np
import onnx
from webdnn.constant_codec_eightbit import compress_tensor_eightbit

FILE_SIGNATURE = b"WDN2"
TENSOR_SIGNATURE = b"TENS"
CLOSE_SIGNATURE = b"CLOS"

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

def _data_type_from_numpy(np_dtype) -> int:
    # dict like {np.float32: 1} cannot be used due to key equality check
    for k, v in DATA_TYPE_TO_NUMPY.items():
        if v == np_dtype:
            return k
    raise ValueError

def _compress_tensor_raw(data: np.ndarray) -> bytes:
    return data.tobytes()

def _compress_tensor(data: np.ndarray, compression_algorithm: int) -> bytes:
    if compression_algorithm == 0:
        return _compress_tensor_raw(data)
    elif compression_algorithm == 1:
        return compress_tensor_eightbit(data)
    else:
        raise ValueError

def _select_compression_algorithm(data: np.ndarray, compression_algorithm: int) -> int:
    if data.dtype != np.float32:
        return 0
    return compression_algorithm

def _make_tensor_chunk(name: str, data: np.ndarray, compression_algorithm: int) -> bytes:
    data_type = _data_type_from_numpy(data.dtype)
    compression_algorithm = _select_compression_algorithm(data, compression_algorithm)
    compressed_body = _compress_tensor(data, compression_algorithm)
    compressed_body_size = len(compressed_body)
    ndim = data.ndim
    dims = data.shape
    name_bytes = name.encode("utf-8")
    name_length = len(name_bytes)
    extra_bytes = b""
    extra_length = len(extra_bytes)
    header = struct.pack("<BIBB",
        compression_algorithm,
        compressed_body_size,
        data_type,
        ndim)
    header += struct.pack("<" + "I" * len(dims), *dims)
    header += struct.pack("<I", name_length)
    header += name_bytes
    header += struct.pack("<I", extra_length)
    header += extra_bytes
    header += compressed_body
    header = TENSOR_SIGNATURE + struct.pack("<I", len(header)) + header
    return header

def _make_close_chunk() -> bytes:
    return CLOSE_SIGNATURE + b"\0\0\0\0"

def serialize_tensors(path_template: str, tensors: Dict[str, np.ndarray], split_size: int=0, compression_algorithm: int=0) -> List[str]:
    chunks = [FILE_SIGNATURE]
    for name, data in tensors.items():
        chunks.append(_make_tensor_chunk(name, data, compression_algorithm))
    chunks.append(_make_close_chunk())
    full_data = b"".join(chunks)
    if split_size <= 0:
        with open(path_template, "wb") as f:
            f.write(full_data)
        return [path_template]
    else:
        file_paths = []
        for i in range((len(full_data) + split_size - 1) // split_size):
            file_path = path_template.format(i)
            file_paths.append(file_path)
            with open(file_path, "wb") as f:
                f.write(full_data[i*split_size:(i+1)*split_size])
        return file_paths

def _tensor_proto_to_numpy(tensor_proto: onnx.TensorProto) -> np.ndarray:
    shape = tuple(tensor_proto.dims)
    dtype = DATA_TYPE_TO_NUMPY[tensor_proto.data_type]
    array = np.frombuffer(tensor_proto.raw_data, dtype=dtype).reshape(shape)
    if dtype == np.int64:
        array = np.clip(array, -2**31, 2**31-1).astype(np.int32)
    elif dtype == np.uint64:
        array = np.clip(array, 0, 2**32-1).astype(np.uint32)
    return array

def export_initializers(path_template: str, model: onnx.ModelProto, split_size: int=0, compression_algorithm: int=0) -> List[str]:
    tensors = {}
    initializers = model.graph.initializer
    while len(initializers) > 0:
        tensor_proto = initializers.pop()
        tensors[tensor_proto.name] = _tensor_proto_to_numpy(tensor_proto)
    return serialize_tensors(path_template, tensors, split_size, compression_algorithm)
