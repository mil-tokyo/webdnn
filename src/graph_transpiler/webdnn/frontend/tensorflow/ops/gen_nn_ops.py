import tensorflow as tf

from webdnn.frontend.tensorflow.converter import TensorFlowConverter
from webdnn.frontend.tensorflow.util import unary_op_handler, check_data_format, convert_odd_padding_to_concat, parse_padding
from webdnn.graph.axis import Axis
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.clipped_relu import ClippedRelu
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.softplus import Softplus
from webdnn.graph.operators.softsign import Softsign
from webdnn.graph.order import Order
from webdnn.util import console


def padding_same(in_size: int, ksize: int, stride: int) -> int:
    # https://www.tensorflow.org/api_guides/python/nn#Notes_on_SAME_Convolution_Padding
    if in_size % stride == 0:
        pad_total = max(ksize - stride, 0)
    else:
        pad_total = max(ksize - in_size % stride, 0)
    pad_one_size = pad_total // 2 + pad_total % 2
    return pad_one_size


@TensorFlowConverter.register_handler("AvgPool")
def avg_pool_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    data_format = tf_op.get_attr("data_format")
    check_data_format(x, data_format)

    ksize = tuple(tf_op.get_attr("ksize"))  # type: Tuple[int,...]
    assert ksize[x.order.axes_dict[Axis.N]] == 1
    assert ksize[x.order.axes_dict[Axis.C]] == 1
    ksize = (ksize[x.order.axes_dict[Axis.H]], ksize[x.order.axes_dict[Axis.W]])

    stride = tuple(tf_op.get_attr("strides"))  # type: Tuple[int,...]
    assert stride[x.order.axes_dict[Axis.N]] == 1
    assert stride[x.order.axes_dict[Axis.C]] == 1
    stride = (stride[x.order.axes_dict[Axis.H]], stride[x.order.axes_dict[Axis.W]])

    paddings = (
        parse_padding(tf_op.get_attr("padding"), ksize[0], 1),
        parse_padding(tf_op.get_attr("padding"), ksize[1], 1),
    )
    x, paddings = convert_odd_padding_to_concat(x, paddings=paddings)

    if any(p > 0 for p in paddings):
        console.warning(
            "[KerasConverter] keras.layers.AveragePooling computes average by dividing number of valid elements in window "
            "(without padding element), but WebDNN divides it by the number of elements including padding element, so different "
            "result will be generated on the edge.")

    y, = AveragePooling2D(None, ksize=ksize, stride=stride, padding=paddings, cover_all=False)(x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("AvgPool3D")
def avg_pool3_d_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("AvgPool3DGrad")
def avg_pool3_d_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("AvgPoolGrad")
def avg_pool_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("BatchNormWithGlobalNormalization")
def batch_norm_with_global_normalization_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("BatchNormWithGlobalNormalizationGrad")
def batch_norm_with_global_normalization_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("BiasAdd")
def bias_add_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    b = converter.get_variable(tf_op.inputs[1])
    data_format = tf_op.get_attr("data_format")

    if data_format == b"NCHW":
        b.order.axes[0].unify(x.order.axes[1])

    elif data_format == b"NHWC":
        b.order.axes[0].unify(x.order.axes[-1])

    else:
        raise NotImplementedError("Unknown data format")

    y = x + b
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("BiasAddGrad")
def bias_add_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("BiasAddV1")
def bias_add_v1_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Conv2D")
def conv2_d_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    data_format = tf_op.get_attr("data_format")
    check_data_format(x, data_format)

    w = converter.get_variable(tf_op.inputs[1])  # HWCN
    w.order.unify(Order([Axis.KH, Axis.KW, Axis.C, Axis.N]))

    ksize = (w.shape_dict[Axis.KH], w.shape_dict[Axis.KW])

    stride = tuple(tf_op.get_attr("strides"))  # type: Tuple[int,...]
    assert stride[x.order.axes_dict[Axis.N]] == 1
    assert stride[x.order.axes_dict[Axis.C]] == 1
    stride = (stride[x.order.axes_dict[Axis.H]], stride[x.order.axes_dict[Axis.W]])

    paddings = (
        parse_padding(tf_op.get_attr("padding"), ksize[0], 1),
        parse_padding(tf_op.get_attr("padding"), ksize[1], 1),
    )
    x, paddings = convert_odd_padding_to_concat(x, paddings=paddings)

    y, = Convolution2D(None, ksize=ksize, stride=stride, padding=paddings)(x, w)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Conv2DBackpropFilter")
def conv2_d_backprop_filter_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Conv2DBackpropInput")
def conv2_d_backprop_input_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # The first argument (input_sizes) is not needed
    # input_sizes = converter.get_variable(tf_op.inputs[0])

    w = converter.get_variable(tf_op.inputs[1])  # HWNC
    w.order.unify(Order([Axis.KH, Axis.KW, Axis.N, Axis.C]))

    gy = converter.get_variable(tf_op.inputs[2])  # NHWC
    data_format = tf_op.get_attr("data_format")
    check_data_format(gy, data_format)

    ksize = (w.shape_dict[Axis.KH], w.shape_dict[Axis.KW])

    stride = tuple(tf_op.get_attr("strides"))  # type: Tuple[int,...]
    assert stride[gy.order.axes_dict[Axis.N]] == 1
    assert stride[gy.order.axes_dict[Axis.C]] == 1
    stride = (stride[gy.order.axes_dict[Axis.H]], stride[gy.order.axes_dict[Axis.W]])

    paddings = (
        parse_padding(tf_op.get_attr("padding"), ksize[0], 1),
        parse_padding(tf_op.get_attr("padding"), ksize[1], 1),
    )

    if any(p[0] != p[1] for p in paddings):
        pad_col2im = tuple(p[0] if p[0] == p[1] else 0 for p in paddings)
        pad_extra = tuple((0, 0) if p[0] == p[1] else p for p in paddings)
        x, = Deconvolution2D(None, ksize=ksize, stride=stride, padding=pad_col2im)(gy, w)

        if data_format == b"NCHW":
            x = x[:, :, pad_extra[0][0]:-pad_extra[0][1], pad_extra[1][0]:-pad_extra[1][1]]

        elif data_format == b"NHWC":
            x = x[:, pad_extra[0][0]:-pad_extra[0][1], pad_extra[1][0]:-pad_extra[1][1], :]

        else:
            raise NotImplementedError(f"Unknown data format: {data_format}")

    else:
        x, = Deconvolution2D(None, ksize=ksize, stride=stride, padding=tuple(p[0] for p in paddings))(gy, w)

    converter.set_variable(tf_op.outputs[0], x)


@TensorFlowConverter.register_handler("Conv3D")
def conv3_d_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Conv3DBackpropFilter")
def conv3_d_backprop_filter_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Conv3DBackpropFilterV2")
def conv3_d_backprop_filter_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Conv3DBackpropInput")
def conv3_d_backprop_input_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Conv3DBackpropInputV2")
def conv3_d_backprop_input_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("DepthwiseConv2dNative")
def depthwise_conv2d_native_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("DepthwiseConv2dNativeBackpropFilter")
def depthwise_conv2d_native_backprop_filter_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("DepthwiseConv2dNativeBackpropInput")
def depthwise_conv2d_native_backprop_input_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Dilation2D")
def dilation2_d_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Dilation2DBackpropFilter")
def dilation2_d_backprop_filter_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Dilation2DBackpropInput")
def dilation2_d_backprop_input_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Elu")(unary_op_handler(Elu))


@TensorFlowConverter.register_handler("EluGrad")
def elu_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FractionalAvgPoolGrad")
def fractional_avg_pool_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FractionalMaxPoolGrad")
def fractional_max_pool_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FusedBatchNorm")
def fused_batch_norm_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    scale = converter.get_variable(tf_op.inputs[1])
    offset = converter.get_variable(tf_op.inputs[2])
    mean = converter.get_variable(tf_op.inputs[3])
    variance = converter.get_variable(tf_op.inputs[4])
    epsilon = tf_op.get_attr("epsilon")
    data_format = tf_op.get_attr("data_format")

    if data_format == b"NHWC":
        channel_axis = x.order.axes[3]

    elif data_format == b"NCHW":
        channel_axis = x.order.axes[1]

    else:
        raise NotImplementedError("Unknown data format")

    scale.order.axes[0].unify(channel_axis)
    offset.order.axes[0].unify(channel_axis)
    mean.order.axes[0].unify(channel_axis)
    variance.order.axes[0].unify(channel_axis)

    y = (x - mean) / ((variance + epsilon) ** 0.5) * scale + offset

    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("FusedPadConv2D")
def fused_pad_conv2_d_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FusedResizeAndPadConv2D")
def fused_resize_and_pad_conv2_d_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("InTopK")
def in_top_k_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("InTopKV2")
def in_top_kv2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("L2Loss")
def l2_loss_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("LRN")
def lrn_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("LRNGrad")
def lrn_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("LogSoftmax")
def log_softmax_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MaxPool")
def max_pool_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    data_format = tf_op.get_attr("data_format")
    check_data_format(x, data_format)

    ksize = tuple(tf_op.get_attr("ksize"))  # type: Tuple[int,...]
    assert ksize[x.order.axes_dict[Axis.N]] == 1
    assert ksize[x.order.axes_dict[Axis.C]] == 1
    ksize = (ksize[x.order.axes_dict[Axis.H]], ksize[x.order.axes_dict[Axis.W]])

    stride = tuple(tf_op.get_attr("strides"))  # type: Tuple[int,...]
    assert stride[x.order.axes_dict[Axis.N]] == 1
    assert stride[x.order.axes_dict[Axis.C]] == 1
    stride = (stride[x.order.axes_dict[Axis.H]], stride[x.order.axes_dict[Axis.W]])

    paddings = (
        parse_padding(tf_op.get_attr("padding"), ksize[0], 1),
        parse_padding(tf_op.get_attr("padding"), ksize[1], 1),
    )
    x, paddings = convert_odd_padding_to_concat(x, paddings=paddings, value=-1.0e10)

    y, = MaxPooling2D(None, ksize=ksize, stride=stride, padding=paddings, cover_all=False)(x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("MaxPool3D")
def max_pool3_d_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MaxPool3DGrad")
def max_pool3_d_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MaxPool3DGradGrad")
def max_pool3_d_grad_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MaxPoolGrad")
def max_pool_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MaxPoolGradGrad")
def max_pool_grad_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MaxPoolGradGradWithArgmax")
def max_pool_grad_grad_with_argmax_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MaxPoolGradWithArgmax")
def max_pool_grad_with_argmax_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MaxPoolWithArgmax")
def max_pool_with_argmax_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedAvgPool")
def quantized_avg_pool_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedBatchNormWithGlobalNormalization")
def quantized_batch_norm_with_global_normalization_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedBiasAdd")
def quantized_bias_add_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedConv2D")
def quantized_conv2_d_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedMaxPool")
def quantized_max_pool_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedRelu")
def quantized_relu_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedRelu6")
def quantized_relu6_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedReluX")
def quantized_relu_x_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Relu")(unary_op_handler(Relu))


@TensorFlowConverter.register_handler("Relu6")
def relu6_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y, = ClippedRelu(None, cap=6)(x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Relu6Grad")
def relu6_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReluGrad")
def relu_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Softmax")
def softmax_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y, = Softmax(None, axis=x.order.axes[-1])(x)

    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("SoftmaxCrossEntropyWithLogits")
def softmax_cross_entropy_with_logits_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Softplus")
def softplus_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y, = Softplus(None, beta=1)(x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("SoftplusGrad")
def softplus_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Softsign")(unary_op_handler(Softsign))


@TensorFlowConverter.register_handler("SoftsignGrad")
def softsign_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SparseSoftmaxCrossEntropyWithLogits")
def sparse_softmax_cross_entropy_with_logits_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("TopK")
def top_k_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("TopKV2")
def top_kv2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")
