from typing import List

import tensorflow as tf

from webdnn.frontend.constraints import unify, unify_order
from webdnn.frontend.tensorflow.converter import TensorFlowConverter
from webdnn.frontend.tensorflow.util import unary_op_handler
from webdnn.graph.axis import Axis
from webdnn.graph.operators.clipped_relu import ClippedRelu
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.softplus import Softplus
from webdnn.graph.operators.softsign import Softsign
from webdnn.graph.order import OrderHWCN, OrderNHWC, OrderC
from webdnn.util import flags


def padding_same(width: int, ksize: int, stride: int) -> int:
    # https://www.tensorflow.org/api_guides/python/nn#Notes_on_SAME_Convolution_Padding
    if width % stride == 0:
        pad_total = max(ksize - stride, 0)
    else:
        pad_total = max(ksize - width % stride, 0)
    pad_one_size = pad_total // 2 + pad_total % 2
    return pad_one_size


@TensorFlowConverter.register_handler("AvgPool")
def avg_pool_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


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
    unify_order(b.order, OrderC)
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
    # FIXME
    x = converter.get_variable(tf_op.inputs[0])  # NHWC
    w = converter.get_variable(tf_op.inputs[1])  # HWCN
    assert tf_op.get_attr("data_format") == b"NHWC"
    unify_order(x.order, OrderNHWC)
    unify_order(w.order, OrderHWCN)
    ksize = (w.shape_dict[Axis.H], w.shape_dict[Axis.W])

    stride_nhwc = tf_op.get_attr("strides")  # type: List[int]
    assert stride_nhwc[0] == 1
    assert stride_nhwc[3] == 1
    stride_hw = stride_nhwc[1:3]
    padding_name = tf_op.get_attr("padding")  # type: str
    if padding_name == b"SAME":
        padding = (padding_same(x.shape_dict[Axis.H], ksize[0], stride_hw[0]),
                   padding_same(x.shape_dict[Axis.W], ksize[1], stride_hw[1]))
    elif padding_name == b"VALID":
        padding = (0, 0)
    else:
        raise NotImplementedError(f"[TensorFlowConverter] Conv2D: padding '{padding_name}' is not supported yet.")

    y, = Convolution2D(None, ksize=ksize, stride=stride_hw, padding=padding)(x, w)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Conv2DBackpropFilter")
def conv2_d_backprop_filter_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Conv2DBackpropInput")
def conv2_d_backprop_input_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


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
    # FIXME
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


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
    # padding: https://www.tensorflow.org/api_guides/python/nn#Notes_on_SAME_Convolution_Padding

    x = converter.get_variable(tf_op.inputs[0])  # NHWC
    assert tf_op.get_attr("data_format") == b"NHWC"
    unify_order(x.order, OrderNHWC)
    ksize_nhwc = tf_op.get_attr("ksize")  # type: List[int]
    assert ksize_nhwc[0] == 1
    assert ksize_nhwc[3] == 1
    ksize = (ksize_nhwc[1], ksize_nhwc[2])

    stride_nhwc = tf_op.get_attr("strides")  # type: List[int]
    assert stride_nhwc[0] == 1
    assert stride_nhwc[3] == 1
    stride_hw = stride_nhwc[1:3]
    padding_name = tf_op.get_attr("padding")  # type: str
    if padding_name == b"SAME":
        padding = (padding_same(x.shape_dict[Axis.H], ksize[0], stride_hw[0]),
                   padding_same(x.shape_dict[Axis.W], ksize[1], stride_hw[1]))
    elif padding_name == b"VALID":
        padding = (0, 0)
    else:
        raise NotImplementedError(f"[TensorFlowConverter] MaxPool: padding '{padding_name}' is not supported yet.")

    y, = MaxPooling2D(None, ksize=ksize, stride=stride_hw, padding=padding)(x)
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

    if flags.AGGRESSIVE_ORDER_INFERENCE:
        # Assumption: Softmax is computed along to Axis.C
        unify(x.order.axes[-1], Axis.C)

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
