import keras


class SquareLayer(keras.layers.Layer):
    """
    calculate x^2 elementwisely
    """

    # noinspection PyMethodOverriding
    def call(self, x):
        return keras.backend.pow(x, 2)
