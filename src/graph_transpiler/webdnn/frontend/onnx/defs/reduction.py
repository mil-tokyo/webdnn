"""
https://github.com/onnx/onnx/blob/09ada0f107f1cc1877f9194475c98d2d8512e188/onnx/defs/reduction/defs.cc
"""

from webdnn.frontend.onnx.converter import ONNXConverter, attribute_dict
from webdnn.frontend.onnx.type_hint import INodeProto
from webdnn.graph.operators.arg_max import ArgMax
from webdnn.graph.operators.arg_min import ArgMin
from webdnn.graph.operators.exp import Exp
from webdnn.graph.operators.log import Log
from webdnn.graph.operators.max import Max
from webdnn.graph.operators.min import Min
from webdnn.graph.operators.prod import Prod
from webdnn.graph.operators.sum import Sum


@ONNXConverter.register_handler("ReduceMax")
def _convert_reduce_max(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])

    attrs = attribute_dict(onnx_op)
    axes = attrs["axes"].ints
    keepdims = (attrs["keepdims"].i if "keepdims" in attrs else 1) == 1
    for a in axes:
        x, = Max(None, axis=x.order.axes[a])(x)

    if not keepdims:
        x = x.squeeze(axis=[x.order.axes[i] for i in axes])

    converter.set_variable(onnx_op.output[0], x)


@ONNXConverter.register_handler("ReduceMin")
def _convert_reduce_min(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])

    attrs = attribute_dict(onnx_op)
    axes = attrs["axes"].ints
    keepdims = (attrs["keepdims"].i if "keepdims" in attrs else 1) == 1
    for a in axes:
        x, = Min(None, axis=x.order.axes[a])(x)

    if not keepdims:
        x = x.squeeze(axis=[x.order.axes[i] for i in axes])

    converter.set_variable(onnx_op.output[0], x)


@ONNXConverter.register_handler("ReduceSum")
def _convert_reduce_sum(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])

    attrs = attribute_dict(onnx_op)
    axes = attrs["axes"].ints
    keepdims = (attrs["keepdims"].i if "keepdims" in attrs else 1) == 1
    for a in axes:
        x, = Sum(None, axis=x.order.axes[a])(x)

    if not keepdims:
        x = x.squeeze(axis=[x.order.axes[i] for i in axes])

    converter.set_variable(onnx_op.output[0], x)


@ONNXConverter.register_handler("ReduceMean")
def _convert_reduce_mean(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])

    attrs = attribute_dict(onnx_op)
    axes = attrs["axes"].ints
    keepdims = (attrs["keepdims"].i if "keepdims" in attrs else 1) == 1
    divisor = 1
    for a in axes:
        divisor *= x.shape[a]
        x, = Sum(None, axis=x.order.axes[a])(x)

    if not keepdims:
        x = x.squeeze(axis=[x.order.axes[i] for i in axes])

    x /= divisor
    converter.set_variable(onnx_op.output[0], x)


@ONNXConverter.register_handler("ReduceProd")
def _convert_reduce_prod(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])

    attrs = attribute_dict(onnx_op)
    axes = attrs["axes"].ints
    keepdims = (attrs["keepdims"].i if "keepdims" in attrs else 1) == 1
    for a in axes:
        x, = Prod(None, axis=x.order.axes[a])(x)

    if not keepdims:
        x = x.squeeze(axis=[x.order.axes[i] for i in axes])

    converter.set_variable(onnx_op.output[0], x)


@ONNXConverter.register_handler("ReduceLogSumExp")
def _convert_reduce_logsumexp(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])
    attrs = attribute_dict(onnx_op)
    axes = [x.order.axes[i] for i in attrs["axes"].ints]
    keepdims = (attrs["keepdims"].i if "keepdims" in attrs else 1) == 1

    max_x = x
    for axis in axes:
        max_x, = Max(None, axis=axis)(max_x)
    exp_delta_x, = Exp(None)(x - max_x)

    sum_exp_delta_x = exp_delta_x
    for axis in axes:
        sum_exp_delta_x, = Sum(None, axis=axis)(sum_exp_delta_x)

    y = Log(None)(sum_exp_delta_x)[0] + max_x

    if not keepdims:
        y = y.squeeze(axis=axes)

    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("ArgMax")
def _convert_argmax(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])

    attrs = attribute_dict(onnx_op)
    axis = attrs["axis"].i
    keepdims = (attrs["keepdims"].i if "keepdims" in attrs else 1) == 1
    x, = ArgMax(None, axis=x.order.axes[axis])(x)

    if not keepdims:
        x = x.squeeze(axis=x.order.axes[axis])

    converter.set_variable(onnx_op.output[0], x)


@ONNXConverter.register_handler("ArgMin")
def _convert_argmin(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])

    attrs = attribute_dict(onnx_op)
    axis = attrs["axis"].i
    keepdims = (attrs["keepdims"].i if "keepdims" in attrs else 1) == 1
    x, = ArgMin(None, axis=x.order.axes[axis])(x)

    if not keepdims:
        x = x.squeeze(axis=x.order.axes[axis])

    converter.set_variable(onnx_op.output[0], x)
