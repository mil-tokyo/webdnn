import chainer
import numpy as np

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.operators.exp import Exp
from webdnn.graph.operators.log import Log
from webdnn.graph.operators.max import Max
from webdnn.graph.operators.sum import Sum
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.order import Order
from webdnn.util import console


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("BatchL2NormSquared")
def _convert_batch_l2_norm_squared(converter: ChainerConverter, c_op: "chainer.functions.BatchL2NormSquared"):
    # TODO
    raise NotImplementedError("[ChainerConverter] BatchL2NormSquared is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Ceil")
def _convert_ceil(converter: ChainerConverter, c_op: "chainer.functions.Ceil"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Ceil is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Clip")
def _convert_clip(converter: ChainerConverter, c_op: "chainer.functions.Clip"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Clip is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("BatchDet")
def _convert_batch_det(converter: ChainerConverter, c_op: "chainer.functions.BatchDet"):
    # TODO
    raise NotImplementedError("[ChainerConverter] BatchDet is not supported")


@ChainerConverter.register_handler("Exp")
def _convert_exp(converter: ChainerConverter, c_op: "chainer.functions.Exp"):
    x = converter.get_variable(c_op.inputs[0])
    y, = Exp(None)(x)
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Log")
def _convert_log(converter: ChainerConverter, c_op: "chainer.functions.Log"):
    x = converter.get_variable(c_op.inputs[0])
    y, = Log(None)(x)
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Log10")
def _convert_log10(converter: ChainerConverter, c_op: "chainer.functions.Log10"):
    x = converter.get_variable(c_op.inputs[0])
    y, = Log(None)(x) / np.log(10)
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Log2")
def _convert_log2(converter: ChainerConverter, c_op: "chainer.functions.Log2"):
    x = converter.get_variable(c_op.inputs[0])
    y, = Log(None)(x) / np.log(2)
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Expm1")
def _convert_expm1(converter: ChainerConverter, c_op: "chainer.functions.Expm1"):
    console.warning("[ChainerConverter] In WebDNN, \"Expm1(x)\" is converted into \"Exp(x)-1\", which is not enough accurate as Expm1 when"
                    "x is so small that \"Exp(x) == 1\" in floating point accuracy.")
    x = converter.get_variable(c_op.inputs[0])
    y = Exp(None)(x)[0] - 1
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Floor")
def _convert_floor(converter: ChainerConverter, c_op: "chainer.functions.Floor"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Floor is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Fmod")
def _convert_fmod(converter: ChainerConverter, c_op: "chainer.functions.Fmod"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Fmod is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Cosh")
def _convert_cosh(converter: ChainerConverter, c_op: "chainer.functions.Cosh"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Cosh is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Sinh")
def _convert_sinh(converter: ChainerConverter, c_op: "chainer.functions.Sinh"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Sinh is not supported")


@ChainerConverter.register_handler("Identity")
def _convert_identity(converter: ChainerConverter, c_op: "chainer.functions.Identity"):
    x = converter.get_variable(c_op.inputs[0])
    converter.set_variable(c_op.outputs[0](), x)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("BatchInv")
def _convert_batch_inv(converter: ChainerConverter, c_op: "chainer.functions.BatchInv"):
    # TODO
    raise NotImplementedError("[ChainerConverter] BatchInv is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Inv")
def _convert_inv(converter: ChainerConverter, c_op: "chainer.functions.Inv"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Inv is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("LinearInterpolate")
def _convert_linear_interpolate(converter: ChainerConverter, c_op: "chainer.functions.LinearInterpolate"):
    # TODO
    raise NotImplementedError("[ChainerConverter] LinearInterpolate is not supported")


@ChainerConverter.register_handler("Log1p")
def _convert_log1p(converter: ChainerConverter, c_op: "chainer.functions.Log1p"):
    console.warning("[ChainerConverter] In WebDNN, \"Log1p(x)\" is converted into \"Log(1+x)\", which is not enough accurate as Log1p when"
                    "x is so small that \"1 + x == 1\" in floating point accuracy.")
    x = converter.get_variable(c_op.inputs[0])
    y, = Log(None)(x + 1)
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("LogSumExp")
def _convert_logsumexp(converter: ChainerConverter, c_op: "chainer.functions.LogSumExp"):
    x = converter.get_variable(c_op.inputs[0])

    if c_op.axis is None:
        axes = list(x.order.axes)
    else:
        axes = [x.order.axes[i] for i in c_op.axis]

    max_x = x
    for axis in axes:
        max_x, = Max(None, axis=axis)(max_x)
    exp_delta_x, = Exp(None)(x - max_x)

    sum_exp_delta_x = exp_delta_x
    for axis in axes:
        sum_exp_delta_x, = Sum(None, axis=axis)(sum_exp_delta_x)

    y = Log(None)(sum_exp_delta_x)[0] + max_x
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("BatchMatMul")
def _convert_batch_mat_mul(converter: ChainerConverter, c_op: "chainer.functions.BatchMatMul"):
    # TODO
    raise NotImplementedError("[ChainerConverter] BatchMatMul is not supported")


@ChainerConverter.register_handler("MatMul")
def _convert_mat_mul(converter: ChainerConverter, c_op: "chainer.functions.MatMul"):
    x0 = converter.get_variable(c_op.inputs[0])
    x1 = converter.get_variable(c_op.inputs[1])
    if x0.order.axes[1 if c_op.transa else 0] == x1.order.axes[0 if c_op.transb else 1]:
        x1 = x1.reinterpret_axes(Order([None, None]))

    y, = Tensordot(None, axes=[x0.order.axes[0 if c_op.transa else 1], x1.order.axes[1 if c_op.transb else 0]])(x0, x1)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Maximum")
def _convert_maximum(converter: ChainerConverter, c_op: "chainer.functions.Maximum"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Maximum is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Minimum")
def _convert_minimum(converter: ChainerConverter, c_op: "chainer.functions.Minimum"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Minimum is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("ArgMax")
def _convert_argmax(converter: ChainerConverter, c_op: "chainer.functions.ArgMax"):
    # TODO
    raise NotImplementedError("[ChainerConverter] ArgMax is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("ArgMin")
def _convert_argMin(converter: ChainerConverter, c_op: "chainer.functions.ArgMin"):
    # TODO
    raise NotImplementedError("[ChainerConverter] ArgMin is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Max")
def _convert_max(converter: ChainerConverter, c_op: "chainer.functions.Max"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Max is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Min")
def _convert_min(converter: ChainerConverter, c_op: "chainer.functions.Min"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Min is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Sqrt")
def _convert_sqrt(converter: ChainerConverter, c_op: "chainer.functions.Sqrt"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Sqrt is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Square")
def _convert_square(converter: ChainerConverter, c_op: "chainer.functions.Square"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Square is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("SquaredDifference")
def _convert_squared_difference(converter: ChainerConverter, c_op: "chainer.functions.SquaredDifference"):
    # TODO
    raise NotImplementedError("[ChainerConverter] SquaredDifference is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Sum")
def _convert_sum(converter: ChainerConverter, c_op: "chainer.functions.Sum"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Sum is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Arccos")
def _convert_arccos(converter: ChainerConverter, c_op: "chainer.functions.Arccos"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Arccos is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Arcsin")
def _convert_arcsin(converter: ChainerConverter, c_op: "chainer.functions.Arcsin"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Arcsin is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Arctan")
def _convert_arctan(converter: ChainerConverter, c_op: "chainer.functions.Arctan"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Arctan is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Cos")
def _convert_cos(converter: ChainerConverter, c_op: "chainer.functions.Cos"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Cos is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Sin")
def _convert_sin(converter: ChainerConverter, c_op: "chainer.functions.Sin"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Sin is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Tan")
def _convert_tan(converter: ChainerConverter, c_op: "chainer.functions.Tan"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Tan is not supported")
