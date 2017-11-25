import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.util import check_broadcast_constraints
from webdnn.graph.axis import Axis
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.order import OrderNCHW, Order, OrderC
from webdnn.graph.variables.constant_variable import ConstantVariable


@ChainerConverter.register_handler("BilinearFunction")
def _convert_bilinear_function(converter: ChainerConverter, c_op: "chainer.functions.connection.bilinear.BilinearFunction"):
    # TODO
    raise NotImplementedError("[ChainerConverter] BilinearFunction is not supported")


@ChainerConverter.register_handler("Convolution2DFunction")
def _convert_convolution_2d(converter: ChainerConverter, c_op: "chainer.functions.connection.convolution_2d.Convolution2DFunction"):
    x = converter.get_variable(c_op.inputs[0])
    w = converter.get_variable(c_op.inputs[1])

    x.order.unify(OrderNCHW)
    w.order.unify(Order([Axis.N, Axis.C, Axis.KH, Axis.KW]))

    conv_opr = Convolution2D(None,
                             ksize=(w.shape_dict[Axis.KH], w.shape_dict[Axis.KW]),
                             stride=(c_op.sy, c_op.sx),
                             padding=(c_op.ph, c_op.pw))

    y, = conv_opr(x, w)

    if len(c_op.inputs) == 3:
        # with bias
        b = converter.get_variable(c_op.inputs[2])
        b.order.unify(OrderC)
        y = y + b

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("ConvolutionND")
def _convert_convolution_nd(converter: ChainerConverter, c_op: "chainer.functions.connection.convolution_nd.ConvolutionND"):
    # TODO
    raise NotImplementedError("[ChainerConverter] ConvolutionND is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Deconvolution2DFunction")
def _convert_deconvolution_2d(converter: ChainerConverter, c_op: "chainer.functions.connection.deconvolution_2d.Deconvolution2DFunction"):
    x = converter.get_variable(c_op.inputs[0])
    w = converter.get_variable(c_op.inputs[1])

    x.order.unify(OrderNCHW)
    w.order.unify(Order([Axis.C, Axis.N, Axis.KH, Axis.KW]))

    deconv_opr = Deconvolution2D(None,
                                 ksize=(w.shape_dict[Axis.KH], w.shape_dict[Axis.KW]),
                                 stride=(c_op.sy, c_op.sx),
                                 padding=(c_op.ph, c_op.pw))

    y, = deconv_opr(x, w)

    if len(c_op.inputs) == 3:
        # with bias
        b = converter.get_variable(c_op.inputs[2])
        b.order.unify(OrderC)
        y = y + b

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("DeconvolutionND")
def _convert_deconvolution_nd(converter: ChainerConverter, c_op: "chainer.functions.connection.deconvolution_nd.DeconvolutionND"):
    # TODO
    raise NotImplementedError("[ChainerConverter] DeconvolutionND is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("DepthwiseConvolution2D")
def _convert_depthwise_convolution_2d(converter: ChainerConverter,
                                      c_op: "chainer.functions.connection.depthwise_convolution_2d.DepthwiseConvolution2D"):
    # TODO
    raise NotImplementedError("[ChainerConverter] DepthwiseConvolution2D is not supported")


@ChainerConverter.register_handler("DilatedConvolution2DFunction")
def _convert_selected_item(converter: ChainerConverter,
                           c_op: "chainer.functions.connection.dilated_convolution_2d.DilatedConvolution2DFunction"):
    x = converter.get_variable(c_op.inputs[0])
    w = converter.get_variable(c_op.inputs[1])

    x.order.unify(OrderNCHW)
    w.order.unify(Order([Axis.N, Axis.C, Axis.KH, Axis.KW]))

    # when dx == 1, it means ordinary convolution.
    conv_opr = Convolution2D(None,
                             ksize=(w.shape_dict[Axis.KH], w.shape_dict[Axis.KW]),
                             stride=(c_op.sy, c_op.sx),
                             padding=(c_op.ph, c_op.pw),
                             dilation_rate=(c_op.dx, c_op.dy))

    y, = conv_opr(x, w)

    if len(c_op.inputs) == 3:
        # with bias
        bias = converter.get_variable(c_op.inputs[2])
        bias.order.unify(OrderC)
        y = y + bias

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("EmbedIDFunction")
def _convert_embed_id(converter: ChainerConverter, c_op: "chainer.functions.connection.embed_id.EmbedIDFunction"):
    # TODO
    raise NotImplementedError("[ChainerConverter] EmbedIDFunction is not supported")


@ChainerConverter.register_handler("LinearFunction")
def _convert_linear_function(converter: ChainerConverter, c_op: "chainer.functions.connection.linear.LinearFunction"):
    x = converter.get_variable(c_op.inputs[0])
    w = converter.get_variable(c_op.inputs[1])  # type: ConstantVariable

    y, = Tensordot(None, axes=[x.order.axes[1:], w.order.axes[1]])(x, w)

    if len(c_op.inputs) == 3:
        # with bias
        b = converter.get_variable(c_op.inputs[2])
        check_broadcast_constraints(y, b)
        y = y + b

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("NStepBiGRU")
def _convert_n_step_bigru(converter: ChainerConverter, c_op: "chainer.functions.NStepBiGRU"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NStepBiGRU is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("NStepGRU")
def _convert_n_step_gru(converter: ChainerConverter, c_op: "chainer.functions.NStepGRU"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NStepGRU is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("NStepBiLSTM")
def _convert_n_step_bilstm(converter: ChainerConverter, c_op: "chainer.functions.NStepBiLSTM"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NStepBiLSTM is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("NStepLSTM")
def _convert_n_step_lstm(converter: ChainerConverter, c_op: "chainer.functions.NStepLSTM"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NStepLSTM is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("NStepBiRNNReLU")
def _convert_n_step_birnn_relu(converter: ChainerConverter, c_op: "chainer.functions.NStepBiRNNReLU"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NStepBiRNNReLU is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("NStepBiRNNTanh")
def _convert_n_step_birnn_tanh(converter: ChainerConverter, c_op: "chainer.functions.NStepBiRNNTanh"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NStepBiRNNTanh is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("NStepRNNReLU")
def _convert_n_step_rnn_relu(converter: ChainerConverter, c_op: "chainer.functions.NStepRNNReLU"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NStepRNNReLU is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("NStepRNNTanh")
def _convert_n_step_rnn_tanh(converter: ChainerConverter, c_op: "chainer.functions.NStepRNNTanh"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NStepRNNTanh is not supported")
