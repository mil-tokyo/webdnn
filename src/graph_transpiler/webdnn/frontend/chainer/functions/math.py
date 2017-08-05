import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.operators.exp import Exp


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


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Exp")
def _convert_exp(converter: ChainerConverter, c_op: "chainer.functions.Exp"):
    x = converter.get_variable(c_op.inputs[0])
    y, = Exp(None)(x)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Log")
def _convert_log(converter: ChainerConverter, c_op: "chainer.functions.Log"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Log is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Log10")
def _convert_log10(converter: ChainerConverter, c_op: "chainer.functions.Log10"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Log10 is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Log2")
def _convert_log2(converter: ChainerConverter, c_op: "chainer.functions.Log2"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Log2 is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Expm1")
def _convert_expm1(converter: ChainerConverter, c_op: "chainer.functions.Expm1"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Expm1 is not supported")


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


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Identity")
def _convert_identity(converter: ChainerConverter, c_op: "chainer.functions.Identity"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Identity is not supported")


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


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Log1p")
def _convert_log1p(converter: ChainerConverter, c_op: "chainer.functions.Log1p"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Log1p is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("LogSumExp")
def _convert_logsumexp(converter: ChainerConverter, c_op: "chainer.functions.LogSumExp"):
    # TODO
    raise NotImplementedError("[ChainerConverter] LogSumExp is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("BatchMatMul")
def _convert_batch_mat_mul(converter: ChainerConverter, c_op: "chainer.functions.BatchMatMul"):
    # TODO
    raise NotImplementedError("[ChainerConverter] BatchMatMul is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("MatMul")
def _convert_mat_mul(converter: ChainerConverter, c_op: "chainer.functions.MatMul"):
    # TODO
    raise NotImplementedError("[ChainerConverter] MatMul is not supported")


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
