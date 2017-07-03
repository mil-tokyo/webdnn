from unittest import SkipTest

import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case


def test():
    for kwargs in [
        {"output_dim": 1},
        {"output_dim": 10},
    ]:
        N_VOCABULARY = 30

        x = keras.layers.Input((14,))
        y = keras.layers.Embedding(input_dim=N_VOCABULARY, **kwargs)(x)
        model = keras.models.Model([x], [y])

        vx = np.random.randint(low=0, high=N_VOCABULARY, size=(2, 14))
        vy = model.predict(vx, batch_size=2)

        graph = KerasConverter(batch_size=2).convert(model)

        generate_kernel_test_case(
            description="[keras] Embedding " + (", ".join([f"{k}={v}" for k, v in kwargs.items()])),
            graph=graph,
            backend=["webgpu", "webassembly"],  # FIXME: fallback backend doesn't support ZeroPadding1D
            inputs={graph.inputs[0]: vx},
            expected={graph.outputs[0]: vy},
            raise_skip=False
        )

    raise SkipTest
