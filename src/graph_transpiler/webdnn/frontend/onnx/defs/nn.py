"""
https://github.com/onnx/onnx/blob/09ada0f107f1cc1877f9194475c98d2d8512e188/onnx/defs/nn/defs.cc
"""
from webdnn.graph.axis import Axis
from webdnn.frontend.onnx.converter import ONNXConverter, attribute_dict
from webdnn.frontend.onnx.type_hint import INodeProto
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.max import Max
from webdnn.graph.operators.sum import Sum
from webdnn.graph.order import OrderC, OrderNCHW, Order
from webdnn.util import console
from webdnn.util.misc import mul


@ONNXConverter.register_handler("AveragePool")
def _convert_average_pool(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])
    x.order.unify(OrderNCHW)

    attrs = attribute_dict(onnx_op)
    ksize = list(attrs["kernel_shape"].ints)
    stride = list(attrs["strides"].ints)

    pad = list(attrs["pads"].ints)
    if len(pad) == 2:
        # NOTE:
        # In PyTorch, pads is generated as tuple of 2 integers, but ONNX spec says that pads contains 2*N integers where N is the number of
        # padded dimension. It's maybe PyTorch's bug.
        pass

    else:
        if any(pad[2 * i] != pad[2 * i + 1] for i in range(len(pad) // 2)):
            raise NotImplementedError("[ONNXConverter] odd-size padding is not supported.")
        pad = [pad[0], pad[2]]

    y, = AveragePooling2D(None, ksize=ksize, stride=stride, padding=pad, cover_all=False)(x)
    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("MaxPool")
def _convert_max_pool(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])
    x.order.unify(OrderNCHW)

    attrs = attribute_dict(onnx_op)
    ksize = list(attrs["kernel_shape"].ints)
    stride = list(attrs["strides"].ints)

    pad = list(attrs["pads"].ints)
    if len(pad) == 2:
        # NOTE:
        # In PyTorch, pads is generated as tuple of 2 integers, but ONNX spec says that pads contains 2*N integers where N is the number of
        # padded dimension. It's maybe PyTorch's bug.
        pass

    else:
        if any(pad[2 * i] != pad[2 * i + 1] for i in range(len(pad) // 2)):
            raise NotImplementedError("[ONNXConverter] odd-size padding is not supported.")
        pad = [pad[0], pad[2]]

    # https://github.com/onnx/onnx/blob/master/docs/Operators.md
    # output_spatial_shape[i] = floor((input_spatial_shape[i] + pad_shape[i] - kernel_spatial_shape[i]) / strides_spatial_shape[i] + 1)
    # In PyTorch, nn.MaxPool2d(2) with input size 11 produces output size 5,
    # where kernel_shape=2, pads=0, strides=2 is set as onnx attributes.
    # It corresponds to cover_all=False.
    y, = MaxPooling2D(None, ksize=ksize, stride=stride, padding=pad, cover_all=False)(x)
    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("Conv")
def _convert_conv(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])
    x.order.unify(OrderNCHW)

    w = converter.get_variable(onnx_op.input[1])
    w.order.unify(Order([Axis.N, Axis.C, Axis.KH, Axis.KW]))

    attrs = attribute_dict(onnx_op)
    ksize = list(attrs["kernel_shape"].ints)
    dilations = list(attrs["dilations"].ints)
    stride = list(attrs["strides"].ints)

    pad = list(attrs["pads"].ints)
    if any(pad[2 * i] != pad[2 * i + 1] for i in range(len(pad) // 2)):
        raise NotImplementedError("[ONNXConverter] odd-size padding is not supported.")
    pad = [pad[0], pad[2]]

    y, = Convolution2D(None, ksize=ksize, stride=stride, padding=pad, dilation_rate=dilations)(x, w)
    y.change_order(OrderNCHW)

    if len(onnx_op.input) == 3:
        # with bias
        b = converter.get_variable(onnx_op.input[2])
        b.order.unify(OrderC)
        y = y + b

    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("ConvTranspose")
def _convert_conv_transpose(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"ConvTranspose\" is not supported yet.")


@ONNXConverter.register_handler("GlobalAveragePool")
def _convert_global_average_pool(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])
    if x.ndim == 4:
        x.order.unify(OrderNCHW)

    reduction_size = mul(x.shape[2:])
    reduction_axis = Axis()

    x = x.reshape([x.shape[0], x.shape[1], reduction_size],
                  Order([x.order.axes[0], x.order.axes[1], reduction_axis]))
    y, = Sum(None, axis=reduction_axis)(x)
    y /= reduction_size

    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("GlobalMaxPool")
def _convert_global_max_pool(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])
    if x.ndim == 4:
        x.order.unify(OrderNCHW)

    reduction_size = mul(x.shape[2:])
    reduction_axis = Axis()

    x = x.reshape([x.shape[0], x.shape[1], reduction_size],
                  Order([x.order.axes[0], x.order.axes[1], reduction_axis]))
    y, = Max(None, axis=reduction_axis)(x)

    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("BatchNormalization")
def _convert_batch_normalization(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])
    x.order.axes[0].unify(Axis.N)
    x.order.axes[1].unify(Axis.C)

    scale = converter.get_variable(onnx_op.input[1])
    scale.order.unify(OrderC)

    B = converter.get_variable(onnx_op.input[2])
    B.order.unify(OrderC)

    mean = converter.get_variable(onnx_op.input[3])
    mean.order.unify(OrderC)

    var = converter.get_variable(onnx_op.input[4])
    var.order.unify(OrderC)

    attrs = attribute_dict(onnx_op)
    assert "spatial" not in attrs or attrs["spatial"].i == 1, \
        "[ONNXConverter] Operator \"BatchNormalization\" spatial==0 is not implemented."
    epsilon = attrs["epsilon"].f if "epsilon" in attrs else 1e-5
    y = (x - mean) / ((var + epsilon) ** 0.5) * scale + B
    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("Dropout")
def _convert_max_pool(converter: ONNXConverter, onnx_op: INodeProto):
    console.warning("[ONNXConverter] Operator \"Dropout\" is ignored")
    x = converter.get_variable(onnx_op.input[0])
    converter.set_variable(onnx_op.output[0], x)


@ONNXConverter.register_handler("Flatten")
def _convert_flatten(converter: ONNXConverter, onnx_op: INodeProto):
    x = converter.get_variable(onnx_op.input[0])

    attrs = attribute_dict(onnx_op)
    axis = attrs["axis"].i if "axis" in attrs else 1

    new_shape = [mul(x.shape[:axis]), mul(x.shape[axis:])]
    new_order = Order([None, None])

    y = x.reshape(shape=new_shape, order=new_order)

    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("LRN")
def _convert_lrn(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"LRN\" is not supported yet.")
