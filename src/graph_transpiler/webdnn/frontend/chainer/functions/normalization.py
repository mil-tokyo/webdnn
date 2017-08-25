import chainer

from webdnn import Axis, ConstantVariable
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.constraints import unify_order, unify
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.order import OrderNCHW, OrderC


@ChainerConverter.register_handler("NormalizeL2")
def _convert_normalize_l2(converter: ChainerConverter, c_op: "chainer.functions.NormalizeL2"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NormalizeL2 is not supported")


@ChainerConverter.register_handler("LocalResponseNormalization")
def _convert_local_response_normalization(converter: ChainerConverter,
                                          c_op: "chainer.functions.normalization.local_response_normalization.LocalResponseNormalization"):
    x = converter.get_variable(c_op.inputs[0])
    unify_order(x.order, OrderNCHW)

    n_opr = LocalResponseNormalization(None, n=c_op.n, k=c_op.k, alpha=c_op.alpha, beta=c_op.beta)

    y, = n_opr(x)

    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("BatchNormalizationFunction")
def _convert_batch_normalization_function(converter: ChainerConverter,
                                          c_op: "chainer.functions.normalization.batch_normalization.BatchNormalizationFunction"):
    x = converter.get_variable(c_op.inputs[0])
    unify(x.order.axes[0], Axis.N)
    unify(x.order.axes[1], Axis.C)

    gamma = converter.get_variable(c_op.inputs[1])
    unify_order(gamma.order, OrderC)

    beta = converter.get_variable(c_op.inputs[2])
    unify_order(beta.order, OrderC)

    if len(c_op.inputs) == 5:
        mean = converter.get_variable(c_op.inputs[3])
        unify_order(mean.order, OrderC)

        variance = converter.get_variable(c_op.inputs[4])
        unify_order(variance.order, OrderC)

    elif len(c_op.inputs) == 3:
        mean = 0 if c_op.running_mean is None else ConstantVariable(c_op.running_mean, OrderC)
        variance = 1 if c_op.running_var is None else ConstantVariable(c_op.running_var, OrderC)

    else:
        raise ValueError("inputs to BatchNormalizationFunction have to be 5 or 3.")

    y = (x - mean) / ((variance + c_op.eps) ** 0.5) * gamma + beta
    converter.set_variable(c_op.outputs[0](), y)
