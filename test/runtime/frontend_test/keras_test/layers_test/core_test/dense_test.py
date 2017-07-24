import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(activation=None, use_bias=True, description: str = ""):
    x = keras.layers.Input((4,))
    y = keras.layers.Dense(8, activation=activation, use_bias=use_bias)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 4) - 0.5
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] Dense {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_activation():
    template(activation="relu")


def test_nobias():
    template(use_bias=False)
