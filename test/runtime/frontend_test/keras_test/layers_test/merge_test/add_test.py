import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(description: str = ""):
    x1 = keras.layers.Input((14, 15, 16))
    x2 = keras.layers.Input((14, 15, 16))
    y = keras.layers.Add()([x1, x2])
    model = keras.models.Model([x1, x2], [y])

    vx1 = np.random.rand(2, 14, 15, 16)
    vx2 = np.random.rand(2, 14, 15, 16)
    vy = model.predict([vx1, vx2], batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] Add {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: vx1,
            graph.inputs[1]: vx2
        },
        expected={graph.outputs[0]: vy},
    )


def test():
    template()
