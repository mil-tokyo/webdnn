from unittest import SkipTest

import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case


def test():
    for alpha in [0, 0.5, 1.0]:
        x = keras.layers.Input((4,))
        y = keras.layers.ELU(alpha=alpha)(x)
        model = keras.models.Model([x], [y])

        vx = np.random.rand(2, 4) - 0.5
        vy = model.predict(vx, batch_size=2)

        graph = KerasConverter(batch_size=2).convert(model)

        generate_kernel_test_case(
            description=f"[keras] ELU alpha={alpha}",
            graph=graph,
            inputs={graph.inputs[0]: vx},
            expected={graph.outputs[0]: vy},
            raise_skip=False
        )

    raise SkipTest
