import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x1_shape=[5, 10, 15], x2_shape=[5, 9, 15], axis=2, description: str = ""):
    x1 = keras.layers.Input(x1_shape)
    x2 = keras.layers.Input(x2_shape)
    y = keras.layers.Concatenate(axis=axis)([x1, x2])
    model = keras.models.Model([x1, x2], [y])

    vx1 = np.random.rand(2, *x1_shape)
    vx2 = np.random.rand(2, *x2_shape)
    vy = model.predict([vx1, vx2], batch_size=2)

    graph = KerasConverter(batch_size=2, use_tensorflow_converter=False).convert(model)

    generate_kernel_test_case(
        description=f"[keras] Concat {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: vx1,
            graph.inputs[1]: vx2
        },
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_itself():
    x = keras.layers.Input([5, 10, 15])
    y = keras.layers.Concatenate(axis=2)([x, x])
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 5, 10, 15)
    vy = model.predict([vx], batch_size=2)

    graph = KerasConverter(batch_size=2, use_tensorflow_converter=False).convert(model)

    generate_kernel_test_case(
        description=f"[keras] Concat itself",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )
