import keras


class BiasLayer(keras.layers.Layer):
    """
    Trainable bias layer

    # Input shape
        2D tensor of shape `(num_samples, features)`.

    # Output shape
        2D tensor of shape `(num_samples, features)`.
    """

    def build(self, input_shape):
        self.bias = self.add_weight(name='bias',
                                    shape=(input_shape[-1],),
                                    initializer=keras.initializers.get("uniform"))

    def call(self, x):
        return x + self.bias


# ---------------------------------------------------------------------------------------------------
# Register converter handler

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.axis import Axis
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.order import OrderC


@KerasConverter.register_handler("BiasLayer")
def square_converter_handler(converter, keras_layer):
    keras_x = converter.get_input_tensor(keras_layer)[0]
    webdnn_x = converter.get_variable(keras_x)

    webdnn_b = converter.convert_to_constant_variable(keras_layer.bias, OrderC)
    webdnn_operator = AxiswiseBias(None, axis=Axis.C)

    webdnn_y, = webdnn_operator(webdnn_x, webdnn_b)
    keras_y = converter.get_output_tensor(keras_layer)[0]

    converter.set_variable(keras_y, webdnn_y)
