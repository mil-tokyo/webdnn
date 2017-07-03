from unittest import SkipTest

import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case


def test():
    for kwargs in [
        {},
        # {"use_bias": False}, # FIXME: Not Supported Yet
        # {"stateful": True}, # FIXME: Not Supported Yet
        # {"go_backwards": True}, # FIXME: Not Supported Yet
        {"recurrent_activation": "hard_sigmoid"},
        {"recurrent_activation": "sigmoid"},
        {"return_state": True},
        {"return_sequences": True},
        {"return_state": True, "return_sequences": True},
    ]:
        return_state = ("return_state" in kwargs) and (kwargs["return_state"])

        x = keras.layers.Input((14, 15))
        vx = np.random.rand(2, 14, 15)
        outputs = keras.layers.LSTM(units=16, **kwargs)(x)

        if return_state:
            y, _, c = outputs

            model = keras.models.Model([x], [y, c])
            graph = KerasConverter(batch_size=2).convert(model)

            vy, vc = model.predict(vx, batch_size=2)

            expected = {
                graph.outputs[0]: vy,
                graph.outputs[1]: vc,
            }

        else:
            y = outputs

            model = keras.models.Model([x], [y])
            graph = KerasConverter(batch_size=2).convert(model)

            vy = model.predict(vx, batch_size=2)

            expected = {
                graph.outputs[0]: vy,
            }

        generate_kernel_test_case(
            description="[keras] LSTM " + (", ".join([f"{k}={v}" for k, v in kwargs.items()])),
            graph=graph,
            backend=["webgpu", "webassembly"],  # FIXME: fallback backend doesn't support LSTM
            inputs={graph.inputs[0]: vx},
            expected=expected,
            raise_skip=False
        )

    raise SkipTest
