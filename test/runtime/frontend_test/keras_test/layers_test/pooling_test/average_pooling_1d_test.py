from unittest import SkipTest

import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case


def test():
    for kwargs in [
        {"pool_size": 3, "strides": 1},
        {"pool_size": 3, "strides": 1, "padding": "valid"},
        # different result on edge (webdnn/frontend/keras/layers/pooling.py)
        # {"pool_size": 3, "strides": 1, "padding": "same"},
    ]:
        x = keras.layers.Input((14, 15))
        y = keras.layers.AveragePooling1D(**kwargs)(x)
        model = keras.models.Model([x], [y])

        vx = np.random.rand(2, 14, 15)
        vy = model.predict(vx, batch_size=2)

        graph = KerasConverter(batch_size=2).convert(model)

        generate_kernel_test_case(
            description="[keras] AveragePooling1D " + (", ".join([f"{k}={v}" for k, v in kwargs.items()])),
            graph=graph,
            inputs={graph.inputs[0]: vx},
            expected={graph.outputs[0]: vy},
            raise_skip=False
        )

    raise SkipTest
