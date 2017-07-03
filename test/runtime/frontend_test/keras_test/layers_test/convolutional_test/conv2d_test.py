from unittest import SkipTest

import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case
from webdnn.graph.order import OrderNHWC, OrderNCHW


def test():
    for kwargs in [
        {},
        # {"data_format": "channels_first"}, # FIXME: Not Supported Yet
        {"data_format": "channels_last"},
        {"use_bias": False},
        {"activation": None},
        {"padding": "valid"},
        {"padding": "same"},
        {"dilation_rate": (2, 2)},
    ]:
        channels_first = ("data_format" in kwargs) and (kwargs["data_format"] == "channels_first")

        x = keras.layers.Input((14, 15, 16))
        y = keras.layers.Conv2D(kernel_size=3, filters=8, **kwargs)(x)
        model = keras.models.Model([x], [y])

        vx = np.random.rand(2, 14, 15, 16)
        vy = model.predict(vx, batch_size=2)

        graph = KerasConverter(batch_size=2).convert(model, input_orders=[OrderNCHW if channels_first else OrderNHWC])

        generate_kernel_test_case(
            description="[keras] Conv2D " + (", ".join([f"{k}={v}" for k, v in kwargs.items()])),
            graph=graph,
            inputs={graph.inputs[0]: vx},
            expected={graph.outputs[0]: vy},
            raise_skip=False
        )

    raise SkipTest
