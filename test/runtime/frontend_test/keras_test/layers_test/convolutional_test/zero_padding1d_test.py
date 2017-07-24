import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(padding=1, description: str = ""):
    x = keras.layers.Input((14, 15))
    y = keras.layers.ZeroPadding1D(padding=padding)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 14, 15)
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description=f"[keras] ZeroPadding1D {description}",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
        EPS=1e-2
    )


def test():
    template()


def test_pad_zero():
    template(padding=0)


def test_irregular():
    template(padding=(1, 2))
