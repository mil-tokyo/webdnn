try:
    import keras
except ImportError as e:
    pass

import numpy as np

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.frontend.keras.layers.util import do_activation
from webdnn.graph.axis import Axis
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.order import OrderNC, OrderC, OrderCN, OrderNTC, OrderNHWC
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console
from webdnn.util.misc import mul


@KerasConverter.register_handler("Dense")
def _convert_dense(converter: KerasConverter, k_op: "keras.layers.Dense"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    w = converter.convert_to_constant_variable(k_op.kernel, OrderCN)
    y, = Linear(None)(x, w)

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(k_op.bias, OrderC)
        y = y + b

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Activation")
def _convert_activation(converter: KerasConverter, k_op: "keras.layers.Activation"):
    y = converter.get_variable(converter.get_input_tensor(k_op)[0])

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Dropout")
def _convert_dropout(converter: KerasConverter, k_op: "keras.layers.Dropout"):
    console.warning("[KerasConverter] omitting dropout")

    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    y = x
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Flatten")
def _convert_flatten(converter: KerasConverter, k_op: "keras.layers.Flatten"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    # flatten without changing memory layout
    y, = Reshape(None, in_order=x.order, out_order=OrderNC, out_shape=[x.shape[0], mul(x.shape[1:])])(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


_flag_reshape_first_time = True


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Reshape")
def _convert_reshape(converter: KerasConverter, k_op: "keras.layers.Reshape"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    target_shape = [x.shape[0]] + list(k_op.target_shape)
    if len(target_shape) == 2:
        target_order = OrderNC

    elif len(target_shape) == 3:
        target_order = OrderNTC

    elif len(target_shape) == 4:
        target_order = OrderNHWC

    else:
        raise NotImplementedError(f"[KerasConverter] Unknown default order: shape={target_shape}")

    console.warning("[KerasConverter] keras.layers.Reshape is parsed new data order as default order (OrderNC in 2D, "
                    "OrderNTC in 3D, OrderNHWC in 4D). To handle this, please overwrite keras.layers.Reshape converter "
                    "handler.")

    y, = Reshape(None, in_order=x.order, out_order=target_order, out_shape=target_shape)(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Permute")
def _convert_permute(converter: KerasConverter, k_op: "keras.layers.Permute"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Permute is not supported')


@KerasConverter.register_handler("RepeatVector")
def _convert_repeat_vector(converter: KerasConverter, k_op: "keras.layers.RepeatVector"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    assert x.order == OrderNC, f"[KerasConverter] Currently only OrderNC is supported for input variable order of " \
                               f"keras.layers.RepeatVector: x.order={x.order}"

    N = x.shape_dict[Axis.N]
    n = k_op.n
    C = x.shape_dict[Axis.C]

    # TODO: Implement more efficient version
    # ex) x.shape=(N=2, C=3), n=2
    #
    #  x(N, C)  *      w(C, n*C)     =      y(N, n*C)     =       y(N, n, C)
    # -----------------------------------------------------------------------------
    # [1, 2, 3]   [1, 0, 0, 1, 0, 0]   [1, 2, 3, 1, 2, 3]   [[1, 2, 3], [1, 2, 3]]
    # [4, 5, 6] * [0, 1, 0, 0, 1, 0] = [4, 5, 6, 4, 5, 6] = [[4, 5, 6], [4, 5, 6]]
    #             [0, 0, 1, 0, 0, 1]
    #

    w = ConstantVariable(np.tile(np.eye(C), (1, n)), OrderCN)

    y, = Linear(None)(x, w)
    y, = Reshape(None, in_order=OrderNC, out_order=OrderNTC, out_shape=[N, n, C])(y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Lambda")
def _convert_lambda(converter: KerasConverter, k_op: "keras.layers.Lambda"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Lambda is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("ActivityRegularization")
def _convert_activity_regularization(converter: KerasConverter, k_op: "keras.layers.ActivityRegularization"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.ActivityRegularization is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Masking")
def _convert_masking(converter: KerasConverter, k_op: "keras.layers.Masking"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Masking is not supported')
