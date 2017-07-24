import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(n=5, description: str = ""):
    x = keras.layers.Input((3,))
    y = keras.layers.RepeatVector(n=n)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 3)
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] RepeatVector {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_n_1():
    template(n=1)
