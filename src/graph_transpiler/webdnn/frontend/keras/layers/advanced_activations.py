import keras

from webdnn.frontend.keras import KerasConverter
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.scalar_affine import ScalarAffine


# noinspection PyUnusedLocal
@KerasConverter.register_handler("LeakyReLU")
def _convert_leaky_relu(converter: KerasConverter, k_op: keras.layers.LeakyReLU):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    # FIXME: More effective implementation
    # LeakyReLU(x) = x > 0 ? x : a*x
    #              = (x > 0 ? x : 0) + (x < 0 ? a*x : 0)
    #              = ReLU(x) + (-a) * (-x > 0 ? -x : 0)
    #              = ReLU(x) + (-a) * ReLU(-x)

    y1, = Relu(None)(x)

    y2, = ScalarAffine(None, scale=-1, bias=0)(x)
    y2, = Relu(None)(y2)
    y2, = ScalarAffine(None, scale=-k_op.alpha, bias=0)(y2)

    y, = ElementwiseSum(None)(y1, y2)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("PReLU")
def _convert_prelu(converter: KerasConverter, k_op: keras.layers.PReLU):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.PReLU is not supported')


# noinspection PyUnusedLocal
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
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.ThresholdedReLU is not supported')
