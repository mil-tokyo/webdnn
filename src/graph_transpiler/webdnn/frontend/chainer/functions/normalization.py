import chainer.computational_graph
import numpy as np

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.axis import Axis
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.order import OrderC
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("NormalizeL2")
def _convert_normalize_l2(converter: ChainerConverter, c_op: chainer.functions.NormalizeL2):
    # TODO
    raise NotImplementedError("[ChainerConverter] NormalizeL2 is not supported")


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("LocalResponseNormalization")
def _convert_local_response_normalization(converter: ChainerConverter,
                                          c_op: chainer.functions.normalization.local_response_normalization.LocalResponseNormalization):
    x = converter.get_variable(c_op.inputs[0])

    n_opr = LocalResponseNormalization(None, n=c_op.n, k=c_op.k, alpha=c_op.alpha, beta=c_op.beta)

    y, = n_opr(x)

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("BatchNormalizationFunction")
def _convert_batch_normalization_function(converter: ChainerConverter,
                                          c_op: chainer.functions.normalization.batch_normalization.BatchNormalizationFunction):
    x = converter.get_variable(c_op.inputs[0])
    gamma = converter.get_variable(c_op.inputs[1])
    beta = converter.get_variable(c_op.inputs[2])

    if len(c_op.inputs) == 5:
        # noinspection PyUnresolvedReferences
        mean_data = converter.get_variable(c_op.inputs[3]).data
        # noinspection PyUnresolvedReferences
        variance_data = converter.get_variable(c_op.inputs[4]).data

    elif len(c_op.inputs) == 3:
        variance_data = c_op.running_var
        mean_data = c_op.running_mean

    else:
        raise ValueError("inputs to BatchNormalizationFunction have to be 5 or 3.")
    console.debug(variance_data)

    # Simplify scale and bias
    #
    # from:
    #   y = (x - mean) / sqrt(var + eps) * gamma + beta
    #
    # to:
    #   y = x * gamma_div_std + beta_scaled
    #
    #   gamma_div_std = gamma / sqrt(var + eps)
    #   beta_scaled   = beta - mean * gamma_div_std

    # noinspection PyUnresolvedReferences
    gamma_div_std = gamma.data / np.sqrt(variance_data + c_op.eps)
    # noinspection PyUnresolvedReferences
    beta_scaled = beta.data - mean_data * gamma_div_std

    scale_opr = AxiswiseScale(None, axis=Axis.C)
    gamma_div_std_const = ConstantVariable(gamma_div_std, OrderC)
    scale_out, = scale_opr(x, gamma_div_std_const)

    offset_opr = AxiswiseBias(None, axis=Axis.C)
    beta_scaled_const = ConstantVariable(beta_scaled, OrderC)
    offset_out, = offset_opr(scale_out, beta_scaled_const)

    converter.set_variable(c_op.outputs[0](), offset_out)
