import keras


class SquareLayer(keras.layers.Layer):
    """
    calculate x^2 elementwisely
    """

    # noinspection PyMethodOverriding
    def call(self, x):
        return keras.backend.pow(x, 2)


# ---------------------------------------------------------------------------------------------------
# Step 1. Define custom operator IR to represent your custom layer

from webdnn.graph.operators.elementwise import Elementwise


class SquareOperator(Elementwise):
    pass


# ---------------------------------------------------------------------------------------------------
# Step 2. Register converter handler to convert your keras custom layer into IR

from webdnn.frontend.keras.converter import KerasConverter


@KerasConverter.register_handler("SquareLayer")
def square_converter_handler(converter: KerasConverter, keras_layer: SquareLayer):
    keras_x = converter.get_input_tensor(keras_layer)[0]
    webdnn_x = converter.get_variable(keras_x)

    webdnn_operator = SquareOperator(None)

    webdnn_y, = webdnn_operator(webdnn_x)
    keras_y = converter.get_output_tensor(keras_layer)[0]

    converter.set_variable(keras_y, webdnn_y)


# ---------------------------------------------------------------------------------------------------
# Step 3. Register generator handler to convert IR operator into backend kernel code.
#

from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_fallback
from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_webassembly
from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_webgpu

register_elementwise_kernel_fallback(SquareOperator, "y = x0 * x0;")
register_elementwise_kernel_webassembly(SquareOperator, "y = x0 * x0;")
register_elementwise_kernel_webgpu(SquareOperator, "y = x0 * x0;")
