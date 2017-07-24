import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(activation, description: str = ""):
    x = keras.layers.Input((4,))
    y = keras.layers.Activation(activation)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 4) - 0.5
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] Activation {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test_softmax():
    template("softmax")


def test_elu():
    template("elu")


def test_softplus():
    template("softplus")


def test_softsign():
    template("softsign")


def test_relu():
    template("relu")


def test_tanh():
    template("tanh")


def test_sigmoid():
    template("sigmoid")


def test_hard_sigmoid():
    template("hard_sigmoid")


def test_linear():
    template("linear")
