"""
https://github.com/onnx/onnx/blob/09ada0f107f1cc1877f9194475c98d2d8512e188/onnx/defs/tensor/defs.cc
"""

from webdnn.frontend.onnx.converter import ONNXConverter, attribute_dict
from webdnn.frontend.onnx.type_hint import INodeProto
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.order import Order
from webdnn.util import console
from webdnn.util.misc import mul


@ONNXConverter.register_handler("Cast")
def _convert_cast(converter: ONNXConverter, onnx_op: INodeProto):
    console.warning("[ONNXConverter] Operator \"Cast\" is ignored")
    x = converter.get_variable(onnx_op.input[0])
    converter.set_variable(onnx_op.output[0], x)


@ONNXConverter.register_handler("Reshape")
def _convert_reshape(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])
    attrs = attribute_dict(onnx_op)
    out_shape = [r if s == 0 else s for r, s in zip(x.shape, attrs["shape"].ints)]

    if -1 in out_shape:
        i = out_shape.index(-1)
        out_shape.remove(-1)
        out_shape.insert(i, x.size // mul(out_shape))

    out_order = Order([None] * len(out_shape))

    y, = Reshape(None, in_order=x.order, out_order=out_order, out_shape=out_shape)(x)
    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("Concat")
def _convert_concat(converter: ONNXConverter, onnx_op: INodeProto):
    xs = [converter.get_variable(v) for v in onnx_op.input]
    for x in xs[1:]:
        xs[0].order.unify(x.order)
        
    attrs = attribute_dict(onnx_op)
    axis = xs[0].order.axes[attrs["axis"].i]

    y, = Concat(None, axis=axis)(*xs)
    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("Split")
def _convert_split(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"Split\" is not supported yet.")


@ONNXConverter.register_handler("Slice")
def _convert_slice(converter: ONNXConverter, onnx_op: INodeProto):
    raise NotImplementedError("[ONNXConverter] Operator \"Slice\" is not supported yet.")


@ONNXConverter.register_handler("Transpose")
def _convert_transpose(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])
    attrs = attribute_dict(onnx_op)

    y, = Transpose(None)(x)
    perm = list(attrs["perm"].ints if "perm" in attrs else reversed(range(x.ndim)))
    y.change_order(Order([x.order.axes[i] for i in perm]))

    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("Gather")
def _convert_gather(converter: ONNXConverter, onnx_op: INodeProto):
    raise NotImplementedError("[ONNXConverter] Operator \"Gather\" is not supported yet.")


@ONNXConverter.register_handler("Squeeze")
def _convert_squeeze(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"Squeeze\" is not supported yet.")


@ONNXConverter.register_handler("Pad")
def _convert_pad(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"Pad\" is not supported yet.")
