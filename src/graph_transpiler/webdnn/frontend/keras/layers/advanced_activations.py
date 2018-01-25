import keras

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.leaky_relu import LeakyRelu
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.threshold_relu import ThresholdRelu


@KerasConverter.register_handler("ELU")
def _convert_elu(converter: KerasConverter, k_op: "keras.layers.ELU"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    alpha = float(k_op.alpha)

    if alpha == 1.0:
        y, = Elu(None)(x)

    elif alpha == 0.0:
        y, = Relu(None)(x)

    else:
        y1, = Elu(None)(x)
        y2, = Relu(None)(x)
        y = y1 * alpha + y2 * (1 - alpha)

    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("LeakyReLU")
def _convert_leaky_relu(converter: KerasConverter, k_op: "keras.layers.LeakyReLU"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    if k_op.alpha == 0:
        y, = Relu(None)(x)
    else:
        y, = LeakyRelu(None, slope=k_op.alpha)(x)

    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("PReLU")
def _convert_prelu(converter: KerasConverter, k_op: "keras.layers.PReLU"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.PReLU is not supported')


@KerasConverter.register_handler("ThresholdedReLU")
def _convert_thresholded_relu(converter: KerasConverter, k_op: "keras.layers.ThresholdedReLU"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    if k_op.theta == 0:
        y, = Relu(None)(x)
    else:
        y, = ThresholdRelu(None, threshold=k_op.theta)(x)

    converter.set_variable(converter.get_output_tensor(k_op)[0], y)
