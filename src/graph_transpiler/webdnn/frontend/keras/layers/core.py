import keras

from webdnn.frontend.keras import KerasConverter
from webdnn.frontend.keras.layers.util import do_activation
from webdnn.graph.axis import Axis
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.order import OrderNC, OrderC, OrderCN
from webdnn.util import console
from webdnn.util.misc import mul


@KerasConverter.register_handler("Dense")
def _convert_dense(converter: KerasConverter, k_op: keras.layers.Dense):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    w = converter.convert_to_constant_variable(k_op.kernel, OrderCN)
    y, = Linear(None)(x, w)

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(k_op.bias, OrderC)
        y, = AxiswiseBias(None, Axis.C)(y, b)

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Activation")
def _convert_activation(converter: KerasConverter, k_op: keras.layers.Activation):
    y = converter.get_variable(converter.get_input_tensor(k_op)[0])

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Dropout")
def _convert_dropout(converter: KerasConverter, k_op: keras.layers.Dropout):
    console.warning("[KerasConverter] omitting dropout")

    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    y = x
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Flatten")
def _convert_flatten(converter: KerasConverter, k_op: keras.layers.Flatten):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    # flatten without changing memory layout
    y, = Reshape(None, in_order=x.order, out_order=OrderNC, out_shape=[x.shape[0], mul(x.shape[1:])])(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Reshape")
def _convert_reshape(converter: KerasConverter, k_op: keras.layers.Reshape):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Reshape is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Permute")
def _convert_permute(converter: KerasConverter, k_op: keras.layers.Permute):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Permute is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("RepeatVector")
def _convert_repeat_vector(converter: KerasConverter, k_op: keras.layers.RepeatVector):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.RepeatVector is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Lambda")
def _convert_lambda(converter: KerasConverter, k_op: keras.layers.Lambda):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Lambda is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("ActivityRegularization")
def _convert_activity_regularization(converter: KerasConverter, k_op: keras.layers.ActivityRegularization):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.ActivityRegularization is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Masking")
def _convert_masking(converter: KerasConverter, k_op: keras.layers.Masking):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Masking is not supported')
