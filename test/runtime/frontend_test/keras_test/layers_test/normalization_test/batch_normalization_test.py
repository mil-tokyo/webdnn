from unittest import SkipTest

import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case
from webdnn.graph.order import OrderNHWC, OrderNCHW


def test():
    for kwargs in [
        {},
        {"epsilon": 0.8},
        {"scale": False},
        {"center": False},
    ]:
        x = keras.layers.Input((14, 15, 16))
        y = keras.layers.BatchNormalization(axis=3, **kwargs)(x)
        model = keras.models.Model([x], [y])

        vx = np.random.rand(2, 14, 15, 16)
        vy = model.predict(vx, batch_size=2)

        graph = KerasConverter(batch_size=2).convert(model)

        generate_kernel_test_case(
            description="[keras] BatchNormalization " + (", ".join([f"{k}={v}" for k, v in kwargs.items()])),
            graph=graph,
            inputs={graph.inputs[0]: vx},
            expected={graph.outputs[0]: vy},
            raise_skip=False
        )

    raise SkipTest
