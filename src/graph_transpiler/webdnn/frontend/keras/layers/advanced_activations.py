import keras

from webdnn.frontend.keras import KerasConverter
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.leaky_relu import LeakyRelu
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.threshold_relu import ThresholdRelu


@KerasConverter.register_handler("LeakyReLU")
def _convert_leaky_relu(converter: KerasConverter, k_op: keras.layers.LeakyReLU):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    if k_op.alpha == 0:
        y, = Relu(None)(x)
    else:
        y, = LeakyRelu(None, slope=k_op.alpha)(x)

    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("PReLU")
def _convert_prelu(converter: KerasConverter, k_op: keras.layers.PReLU):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.PReLU is not supported')


@KerasConverter.register_handler("ELU")
def _convert_elu(converter: KerasConverter, k_op: keras.layers.ELU):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    y, = Elu(None)(x)

    if k_op.alpha != 1.0:
        y, = ScalarAffine(None, scale=k_op.alpha, bias=0)(y)

    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("ThresholdedReLU")
def _convert_thresholded_relu(converter: KerasConverter, k_op: keras.layers.ThresholdedReLU):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    if k_op.theta == 0:
        y, = Relu(None)(x)
    else:
        y, = ThresholdRelu(None, threshold=k_op.theta)(x)

    converter.set_variable(converter.get_output_tensor(k_op)[0], y)
