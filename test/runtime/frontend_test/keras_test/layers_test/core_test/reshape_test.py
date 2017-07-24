import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(description: str = ""):
    x = keras.layers.Input((4, 5, 6))
    y = keras.layers.Reshape(target_shape=(12, 10))(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 4, 5, 6)
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] Reshape {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()
