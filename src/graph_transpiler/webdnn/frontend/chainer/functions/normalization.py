import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.axis import Axis
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.order import OrderNCHW, OrderC
from webdnn.graph.variables.constant_variable import ConstantVariable


@ChainerConverter.register_handler("NormalizeL2")
def _convert_normalize_l2(converter: ChainerConverter, c_op: "chainer.functions.NormalizeL2"):
    # TODO
    raise NotImplementedError("[ChainerConverter] NormalizeL2 is not supported")


@ChainerConverter.register_handler("LocalResponseNormalization")
def _convert_local_response_normalization(converter: ChainerConverter,
                                          c_op: "chainer.functions.normalization.local_response_normalization.LocalResponseNormalization"):
    x = converter.get_variable(c_op.inputs[0])
    x.order.unify(OrderNCHW)

    n_opr = LocalResponseNormalization(None, n=c_op.n, k=c_op.k, alpha=c_op.alpha, beta=c_op.beta)

    y, = n_opr(x)

    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("BatchNormalization")
@ChainerConverter.register_handler("BatchNormalizationFunction")
def _convert_batch_normalization_function(converter: ChainerConverter,
                                          c_op: "chainer.functions.normalization.batch_normalization.BatchNormalizationFunction"):
    x = converter.get_variable(c_op.inputs[0])
    x.order.axes[0].unify(Axis.N)
    x.order.axes[1].unify(Axis.C)

    gamma = converter.get_variable(c_op.inputs[1])
    gamma.order.unify(OrderC)

    beta = converter.get_variable(c_op.inputs[2])
    beta.order.unify(OrderC)

    if len(c_op.inputs) == 5:
        mean = converter.get_variable(c_op.inputs[3])
        mean.order.unify(OrderC)

        variance = converter.get_variable(c_op.inputs[4])
        variance.order.unify(OrderC)

    elif len(c_op.inputs) == 3:
        mean = 0 if c_op.running_mean is None else ConstantVariable(c_op.running_mean, OrderC)
        variance = 1 if c_op.running_var is None else ConstantVariable(c_op.running_var, OrderC)

    else:
        raise ValueError("Number of inputs to BatchNormalizationFunction must be 3 or 5.")

    y = (x - mean) / ((variance + c_op.eps) ** 0.5) * gamma + beta
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("FixedBatchNormalization")
def _convert_fixed_batch_normalization(converter: ChainerConverter,
                                       c_op: "chainer.functions.normalization.batch_normalization.FixedBatchNormalization"):
    x = converter.get_variable(c_op.inputs[0])
    x.order.axes[0].unify(Axis.N)
    x.order.axes[1].unify(Axis.C)

    gamma = converter.get_variable(c_op.inputs[1])
    gamma.order.unify(OrderC)

    beta = converter.get_variable(c_op.inputs[2])
    beta.order.unify(OrderC)

    mean = converter.get_variable(c_op.inputs[3])
    mean.order.unify(OrderC)

    variance = converter.get_variable(c_op.inputs[4])
    variance.order.unify(OrderC)

    y = (x - mean) / ((variance + c_op.eps) ** 0.5) * gamma + beta
    converter.set_variable(c_op.outputs[0](), y)
