import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(pool_size=(3, 3), strides=2, padding="valid", data_format=None, description: str = ""):
    x = keras.layers.Input((15, 17, 16))  # (height + pad * 2 - pool_size) % stride == 0 to avoid edge difference
    y = keras.layers.MaxPooling2D(pool_size=pool_size, strides=strides, padding=padding, data_format=data_format)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 15, 17, 16)
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] MaxPooling2D {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_irregular_size():
    template(pool_size=(3, 4), strides=(2, 1))


def test_padding_valid():
    template(padding="valid")

def test_padding_same():
    template(padding="same")
