import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(axis=-1, epsilon=1e-3, center=True, scale=True, description: str = ""):
    x = keras.layers.Input((14, 15, 16))
    y = keras.layers.BatchNormalization(axis=axis, epsilon=epsilon, center=center, scale=scale)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 14, 15, 16)
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] BatchNormalization {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_epsilon():
    template(epsilon=1e-2)


def test_center():
    template(center=False)


def test_scale():
    template(scale=False)
