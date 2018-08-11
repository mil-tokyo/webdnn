"""
Type declaration for ONNX protocol buffer definition
Because python type hinting cannot recognized protobuf type definition, so this declaration is useful.

This declaration is based on https://github.com/onnx/onnx/blob/09ada0f107f1cc1877f9194475c98d2d8512e188/onnx/onnx.proto
"""

from typing import NamedTuple, Sequence, Type, Optional

import numpy as np


# `typing.Sequence` can be regarded as subset of `google.protobuf.pyext._message.RepeatedCompositeContainer` (repeated field of `Message`)

class IAttributeProto(NamedTuple):
    name: str
    type: int

    # Exactly ONE of the following fields must be present for this version of the ONNX IR
    f: float
    i: int
    s: bytes
    t: "ITensorProto"
    g: "IGraphProto"

    floats: Sequence[float]
    ints: Sequence[int]
    strings: bytes
    tensors: Sequence["ITensorProto"]
    graphs: Sequence["IGraphProto"]

    pass


class INodeProto(NamedTuple):
    input: Sequence[str]
    output: Sequence[str]
    name: str
    op_type: str
    attribute: Sequence[IAttributeProto]


class IDimensionProto(NamedTuple):
    dim_value: int


class ITensorShapeProto(NamedTuple):
    dim: Sequence[IDimensionProto]


class ITensorTypeProto(NamedTuple):
    shape: ITensorShapeProto


class ITypeProto(NamedTuple):
    tensor_type: ITensorTypeProto


class IValueInfoProto(NamedTuple):
    name: str
    type: ITypeProto


class ITensorProto(NamedTuple):
    name: str
    data_type: int
    dims: Sequence[int]
    raw_data: bytes


class IGraphProto(NamedTuple):
    initializer: Sequence[ITensorProto]
    input: Sequence[IValueInfoProto]
    node: Sequence[INodeProto]
    output: Sequence[IValueInfoProto]


class IModelProto(NamedTuple):
    graph: IGraphProto


class AttributeType:
    UNDEFINED = 0
    FLOAT = 1
    INT = 2
    STRING = 3
    TENSOR = 4
    GRAPH = 5

    FLOATS = 6
    INTS = 7
    STRINGS = 8
    TENSORS = 9
    GRAPHS = 10


AttributeTypeMappingDict = {
    AttributeType.FLOAT: "f",
    AttributeType.INT: "i",
    AttributeType.STRING: "s",
    AttributeType.TENSOR: "t",
    AttributeType.GRAPH: "g",

    AttributeType.FLOATS: "floats",
    AttributeType.INTS: "ints",
    AttributeType.STRINGS: "strings",
    AttributeType.TENSORS: "tensors",
    AttributeType.GRAPHS: "graphs",
}


class DataType:
    UNDEFINED = 0
    FLOAT = 1
    UINT8 = 2
    INT8 = 3
    UINT16 = 4
    INT16 = 5
    INT32 = 6
    INT64 = 7
    STRING = 8
    BOOL = 9

    FLOAT16 = 10
    DOUBLE = 11
    UINT32 = 12
    UINT64 = 13
    COMPLEX64 = 14
    COMPLEX128 = 15


class NumPyDataType(NamedTuple):
    name: str
    type: Optional[Type]


DataTypeMappingDict = {
    DataType.UNDEFINED: NumPyDataType("", None),
    DataType.FLOAT: NumPyDataType("FLOAT", np.float32),
    DataType.UINT8: NumPyDataType("UINT8", np.uint8),
    DataType.INT8: NumPyDataType("INT8", np.int8),
    DataType.UINT16: NumPyDataType("UINT16", np.uint16),
    DataType.INT16: NumPyDataType("INT16", np.int16),
    DataType.INT32: NumPyDataType("INT32", np.int32),
    DataType.INT64: NumPyDataType("INT64", np.int64),
    DataType.STRING: NumPyDataType("STRING", None),
    DataType.BOOL: NumPyDataType("BOOL", None),

    DataType.FLOAT16: NumPyDataType("FLOAT16", np.float16),
    DataType.DOUBLE: NumPyDataType("DOUBLE", None),
    DataType.UINT32: NumPyDataType("UINT32", np.uint32),
    DataType.UINT64: NumPyDataType("UINT64", np.uint64),
    DataType.COMPLEX64: NumPyDataType("COMPLEX64", None),
    DataType.COMPLEX128: NumPyDataType("COMPLEX128", None),
}
