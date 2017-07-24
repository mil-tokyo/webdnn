import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(pool_size=3, strides=1, padding="valid", description: str = ""):
    x = keras.layers.Input((14, 15))
    y = keras.layers.AveragePooling1D(pool_size=pool_size, strides=strides, padding=padding)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 14, 15)
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] AveragePooling1D {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_padding_valid():
    template(padding="valid")
