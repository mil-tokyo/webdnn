from unittest import SkipTest

import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case


def test():
    for kwargs in [
        # {"use_bias": False}, # FIXME: Not Supported Yet
        # {"stateful": True}, # FIXME: Not Supported Yet
        {"recurrent_activation": "hard_sigmoid"},
        {"recurrent_activation": "sigmoid"}
    ]:
        x = keras.layers.Input((14, 15))
        y = keras.layers.LSTM(unit=16, **kwargs)(x)
        model = keras.models.Model([x], [y])

        vx = np.random.rand(2, 14, 15)
        vy = model.predict(vx, batch_size=2)

        graph = KerasConverter(batch_size=2).convert(model)

        generate_kernel_test_case(
            description="[keras] LSTM " + (", ".join([f"{k}={v}" for k, v in kwargs.items()])),
            graph=graph,
            inputs={graph.inputs[0]: vx},
            expected={graph.outputs[0]: vy},
            raise_skip=False
        )

    raise SkipTest
