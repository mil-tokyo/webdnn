"""
Some of this code is based on codes of ONNX project from follow URL.

https://github.com/onnx/onnx/blob/23b88a1e0f3ac40bb8bf6d82a480eaab83622a8c/onnx/helper.py

-------------------------------------------------------------------------------

Open Neural Network Exchange

Copyright (c) Facebook, Inc. and Microsoft Corporation.
All rights reserved.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the ""Software""), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import numbers
from typing import Sequence, Iterable

import numpy as np
from onnx import TensorProto, AttributeProto, NodeProto, ModelProto, GraphProto, ValueInfoProto

from webdnn.frontend.onnx.type_hint import INodeProto, IAttributeProto, IModelProto, ITensorProto, DataType, IValueInfoProto


def make_attribute(key: str, value) -> IAttributeProto:
    attr = AttributeProto()
    attr.name = key

    is_iterable = isinstance(value, Iterable)
    bytes_or_false = _to_bytes_or_false(value)
    # First, singular cases

    # float
    if isinstance(value, float):
        attr.f = value

    # integer
    elif isinstance(value, numbers.Integral):
        attr.i = value

    # string
    elif bytes_or_false:
        attr.s = bytes_or_false

    elif isinstance(value, TensorProto):
        attr.t.CopyFrom(value)

    elif isinstance(value, GraphProto):
        attr.g.CopyFrom(value)

    # third, iterable cases
    elif is_iterable:
        byte_array = [_to_bytes_or_false(v) for v in value]
        if all(isinstance(v, float) for v in value):
            attr.floats.extend(value)

        elif all(isinstance(v, numbers.Integral) for v in value):
            # Turn np.int32/64 into Python built-in int.
            attr.ints.extend(int(v) for v in value)

        elif all(byte_array):
            attr.strings.extend(byte_array)

        elif all(isinstance(v, TensorProto) for v in value):
            attr.tensors.extend(value)

        elif all(isinstance(v, GraphProto) for v in value):
            attr.graphs.extend(value)

        else:
            raise ValueError(
                "You passed in an iterable attribute but I cannot figure out "
                "its applicable type.")
    else:
        raise ValueError(
            'Value "{}" is not valid attribute data type.'.format(value))

    return attr


def make_node(op_type: str, inputs: Sequence[str], outputs: Sequence[str], **kwargs) -> INodeProto:
    node = NodeProto()
    node.op_type = op_type
    node.input.extend(inputs)
    node.output.extend(outputs)
    node.attribute.extend(make_attribute(key, value) for key, value in kwargs.items())
    return node


def make_model(nodes: Sequence[INodeProto],
               inputs: Sequence[IValueInfoProto],
               outputs: Sequence[IValueInfoProto],
               initializer=None) -> IModelProto:
    if initializer is None:
        initializer = []
    graph = GraphProto()
    graph.node.extend(nodes)
    graph.input.extend(inputs)
    graph.output.extend(outputs)
    graph.initializer.extend(initializer)

    model = ModelProto()
    model.graph.CopyFrom(graph)

    return model


def make_tensor(name: str, vals: np.ndarray) -> ITensorProto:
    """
    Make a TensorProto with specified arguments.  If raw is False, this
    function will choose the corresponding proto field to store the
    values based on data_type. If raw is True, use "raw_data" proto
    field to store the values, and values should be of type bytes in
    this case.
    """
    vals = vals.astype(np.float32)

    tensor = TensorProto()
    tensor.data_type = DataType.FLOAT
    tensor.name = name
    tensor.raw_data = vals.tobytes()
    tensor.dims.extend(vals.shape)
    return tensor


def make_tensor_value_info(name: str, shape: Sequence[int]) -> IValueInfoProto:
    value_info_proto = ValueInfoProto()
    value_info_proto.name = name

    tensor_type_proto = value_info_proto.type.tensor_type
    tensor_type_proto.elem_type = DataType.FLOAT

    tensor_shape_proto = tensor_type_proto.shape.dim

    for d in shape:
        dim = tensor_shape_proto.add()
        dim.dim_value = d

    return value_info_proto


def _to_bytes_or_false(val):
    """
    An internal graph to convert the input to a bytes or to False.
    The criteria for conversion is as follows and should be python 2 and 3
    compatible:
    - If val is py2 str or py3 bytes: return bytes
    - If val is py2 unicode or py3 str: return val.decode('ascii')
    - Otherwise, return False
    """

    if isinstance(val, bytes):
        return val

    else:
        try:
            return val.encode('ascii')

        except AttributeError:
            return False
