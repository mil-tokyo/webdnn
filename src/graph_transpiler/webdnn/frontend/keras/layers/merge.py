import keras

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.select import Select


@KerasConverter.register_handler("Add")
def _convert_add(converter: KerasConverter, k_op: "keras.layers.Add"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    for x in xs[1:]:
        xs[0].order.unify(x.order)

    y, = ElementwiseAdd(None)(*xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Average")
def _convert_average(converter: KerasConverter, k_op: "keras.layers.Average"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    for x in xs[1:]:
        xs[0].order.unify(x.order)

    y = ElementwiseAdd(None)(*xs)[0] / len(xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Concatenate")
def _convert_maximum(converter: KerasConverter, k_op: "keras.layers.Concatenate"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    for x in xs[1:]:
        xs[0].order.unify(x.order)

    y, = Concat(None, axis=xs[0].order.axes[k_op.axis])(*xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Dot")
def _convert_dot(converter: KerasConverter, k_op: "keras.layers.Dot"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Dot is not supported')


@KerasConverter.register_handler("Maximum")
def _convert_maximum(converter: KerasConverter, k_op: "keras.layers.Maximum"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    for x in xs[1:]:
        xs[0].order.unify(x.order)

    y = xs[0]
    for x in xs[1:]:
        cond = y > x
        y, = Select(None)(cond, y, x)

    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Minimum")
def _convert_minimum(converter: KerasConverter, k_op: "keras.layers.Minimum"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    for x in xs[1:]:
        xs[0].order.unify(x.order)

    y = xs[0]
    for x in xs[1:]:
        cond = y > x
        y, = Select(None)(cond, x, y)

    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Multiply")
def _convert_multiply(converter: KerasConverter, k_op: "keras.layers.Multiply"):
    xs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    for x in xs[1:]:
        xs[0].order.unify(x.order)

    y, = ElementwiseMul(None)(*xs)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Subtract")
def _convert_subtract(converter: KerasConverter, k_op: "keras.layers.Subtract"):
    x0 = converter.get_variable(converter.get_input_tensor(k_op)[0])
    x1 = converter.get_variable(converter.get_input_tensor(k_op)[1])
    x0.order.unify(x1.order)

    converter.set_variable(converter.get_output_tensor(k_op)[0], x0 - x1)
