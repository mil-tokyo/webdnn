from webdnn.graph.operators.concat import Concat

try:
    import keras
except ImportError as e:
    pass

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_mul import ElementwiseMul


@KerasConverter.register_handler("Add")
def _convert_add(converter: KerasConverter, k_op: "keras.layers.Add"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]

    y, = ElementwiseAdd(None)(*xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Multiply")
def _convert_multiply(converter: KerasConverter, k_op: "keras.layers.Multiply"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]

    y, = ElementwiseMul(None)(*xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Average")
def _convert_average(converter: KerasConverter, k_op: "keras.layers.Average"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]

    y = ElementwiseAdd(None)(*xs)[0] / len(xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Maximum")
def _convert_maximum(converter: KerasConverter, k_op: "keras.layers.Maximum"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Maximum is not supported')


@KerasConverter.register_handler("Concatenate")
def _convert_maximum(converter: KerasConverter, k_op: "keras.layers.Concatenate"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    y, = Concat(None, axis=xs[0].order.axes[k_op.axis])(*xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Dot")
def _convert_dot(converter: KerasConverter, k_op: "keras.layers.Dot"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Dot is not supported')
