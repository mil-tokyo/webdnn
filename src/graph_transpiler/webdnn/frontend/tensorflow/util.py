from typing import Tuple, Union, Sequence

import numpy as np
import tensorflow as tf

from webdnn.frontend.tensorflow.converter import TensorFlowConverter
from webdnn.frontend.util import check_broadcast_constraints
from webdnn.graph.axis import Axis
from webdnn.graph.operators.concat import Concat
from webdnn.graph.order import OrderNCHW, OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def unary_op_handler(OperatorClass):
    def handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
        x = converter.get_variable(tf_op.inputs[0])
        y, = OperatorClass(None)(x)
        converter.set_variable(tf_op.outputs[0], y)

    return handler


def elementwise_binary_op_handler(OperatorClass, ScalarOperatorClass=None):
    def handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
        a = converter.get_variable(tf_op.inputs[0])
        b = converter.get_variable(tf_op.inputs[1])
        c = None
        if ScalarOperatorClass is not None:
            # Scalar operation if one of the input is constant and scalar
            if isinstance(a, ConstantVariable) and a.size == 1:
                c, = ScalarOperatorClass(None, value=float(a.data[0]))(b)
            elif isinstance(b, ConstantVariable) and b.size == 1:
                c, = ScalarOperatorClass(None, value=float(b.data[0]))(a)

        if c is None:
            # Broadcasting
            check_broadcast_constraints(a, b)

            c, = OperatorClass(None)(a, b)
        converter.set_variable(tf_op.outputs[0], c)

    return handler


def check_data_format(v: Variable, data_format: Union[str, bytes]):
    if isinstance(data_format, str):
        data_format = data_format.lower()

    if data_format == "channels_first" or data_format == b"NCHW":
        v.order.unify(OrderNCHW)

    elif data_format == "channels_last" or data_format == b"NHWC":
        v.order.unify(OrderNHWC)

    else:
        raise ValueError(f"Unknown data format: {data_format}")


def parse_padding(padding_type: str, ksize: int, dilation_rate: int) -> Tuple[int, int]:
    if isinstance(padding_type, str):
        padding_type = padding_type.lower()

    if padding_type == "valid" or padding_type == b"VALID":
        return 0, 0

    elif padding_type == "same" or padding_type == b"SAME":
        # @see https://github.com/tensorflow/tensorflow/blob/e5cf6f0c13b6053e4c58af6a951b204fde263172/tensorflow/python/ops/nn_ops.py#L507-L519
        dilated_ksize = ksize + (ksize - 1) * (dilation_rate - 1)
        pad_extra_size = dilated_ksize - 1
        pad_begin = pad_extra_size // 2
        pad_end = pad_extra_size - pad_begin
        return pad_begin, pad_end

    else:
        raise ValueError(f"Unknown padding: {padding_type}")


def convert_odd_padding_to_concat(x: Variable, padding: Sequence[Tuple[int, int]], value: float = 0.0):
    # Currently WebDNN does not support different-size-padding.
    for i, ((pad_begin, pad_end), axis) in enumerate(zip(padding, (Axis.H, Axis.W))):
        if pad_begin != pad_end:
            xs = []
            if pad_begin > 0:
                data = np.full([pad_begin if a == axis else x.shape_dict[a] for a in x.order.axes], value, dtype=np.float32)
                xs.append(ConstantVariable(data, x.order))

            xs.append(x)

            if pad_end > 0:
                data = np.full([pad_end if a == axis else x.shape_dict[a] for a in x.order.axes], value, dtype=np.float32)
                xs.append(ConstantVariable(data, x.order))

            if len(xs) > 1:
                x, = Concat(None, axis=axis)(*xs)

            padding = tuple((0, 0) if j == i else padding[j] for j in range(len(padding)))

    return x, tuple(p[0] for p in padding)
