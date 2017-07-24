import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(units=16, return_sequences=False, return_state=False, go_backwards=False, stateful=False, activation="tanh",
             recurrent_activation="hard_sigmoid", use_bias=True, description: str = ""):
    x = keras.layers.Input((14, 15))
    vx = np.random.rand(2, 14, 15)
    outputs = keras.layers.LSTM(units=units, return_sequences=return_sequences, return_state=return_state, go_backwards=go_backwards,
                                stateful=stateful, activation=activation, recurrent_activation=recurrent_activation, use_bias=use_bias)(x)

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
        description=f"[keras] LSTM {description}",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx},
        expected=expected,
    )


def test():
    template()


# FIXME: Not supported yet
# def test_nobias():
#     template(use_bias=False)

# FIXME: Not supported yet
# def test_stateful():
#     template(stateful=True)

# FIXME: Not supported yet
# def test_backwards():
#     template(go_backwards=True)

def test_recurrent_activation_hard_sigmoid():
    template(recurrent_activation="hard_sigmoid")


def test_recurrent_activation_sigmoid():
    template(recurrent_activation="sigmoid")


def test_return_state():
    template(return_state=True)


def test_return_sequences():
    template(return_sequences=True)


def test_return_all():
    template(return_state=True, return_sequences=True)
