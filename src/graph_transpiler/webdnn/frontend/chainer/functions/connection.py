import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.util import check_broadcast_constraints
from webdnn.graph.axis import Axis
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.order import OrderNCHW, Order, OrderC
from webdnn.graph.variables.constant_variable import ConstantVariable


# TODO: BilinearFunction

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


# TODO: ConvolutionND

@ChainerConverter.register_handler("Deconvolution2DFunction")
def _convert_deconvolution_2d(converter: ChainerConverter, c_op: "chainer.FunctionNode"):
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


# TODO: DeconvolutionND

# TODO: DepthwiseConvolution2D

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


# TODO: EmbedIDFunction

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

# TODO: NStepBiGRU

# TODO: NStepGRU

# TODO: NStepBiLSTM

# TODO: NStepLSTM

# TODO: NStepBiRNNReLU

# TODO: NStepBiRNNTanh

# TODO: NStepRNNReLU

# TODO: NStepRNNTanh
