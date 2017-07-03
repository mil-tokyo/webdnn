import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case


def test():
    x = keras.layers.Input((14, 15))
    y = keras.layers.GlobalMaxPooling1D()(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, 14, 15)
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2).convert(model)

    generate_kernel_test_case(
        description="[keras] GlobalMaxPooling1D",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy}
    )
