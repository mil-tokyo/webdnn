import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(input_dim=30, output_dim=10, description: str = ""):
    x = keras.layers.Input((14,))
    y = keras.layers.Embedding(input_dim=input_dim, output_dim=output_dim)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.randint(low=0, high=input_dim, size=(2, 14))
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] Embedding {description}",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_input_dim_1():
    template(input_dim=1)


def test_output_dim_1():
    template(output_dim=1)
