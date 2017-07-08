import keras


class PowLayer(keras.layers.Layer):
    """
    calculate x^a elementwisely
    """

    def __init__(self, a, **kwargs):
        super(PowLayer, self).__init__(**kwargs)
        self.a = a

    def call(self, x, **kwargs):
        return keras.backend.pow(x, self.a)


# ---------------------------------------------------------------------------------------------------
# Step 1. Define custom operator IR to represent your custom layer

from webdnn.graph.operators.elementwise import Elementwise


class PowOperator(Elementwise):
    def __init__(self, name, a):
        super(PowOperator, self).__init__(name)
        self.parameters["a"] = a


# ---------------------------------------------------------------------------------------------------
# Step 2. Register converter handler to convert your keras custom layer into IR

from webdnn.frontend.keras.converter import KerasConverter


@KerasConverter.register_handler("PowLayer")
def square_converter_handler(converter, keras_layer):
    keras_x = converter.get_input_tensor(keras_layer)[0]
    webdnn_x = converter.get_variable(keras_x)

    webdnn_operator = PowOperator(None, keras_layer.a)

    webdnn_y, = webdnn_operator(webdnn_x)
    keras_y = converter.get_output_tensor(keras_layer)[0]

    converter.set_variable(keras_y, webdnn_y)


# ---------------------------------------------------------------------------------------------------
# Step 3. Register generator handler to convert IR operator into backend kernel code.

from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_fallback
from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_webassembly
from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_webgpu

register_elementwise_kernel_fallback(PowOperator,
                                     "y = Math.pow(x0, a);",
                                     {"a": lambda op: op.parameters["a"]})

register_elementwise_kernel_webassembly(PowOperator,
                                        "y = powf(x0, a);",
                                        {"a": lambda op: op.parameters["a"]})

register_elementwise_kernel_webgpu(PowOperator,
                                   "y = pow(x0, a);",
                                   {"a": lambda op: op.parameters["a"]})
