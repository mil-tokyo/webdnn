import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(shape=(14, 15, 4), filters=5, kernel_size=3, strides=(1, 1), padding='valid', data_format="channels_last",
             dilation_rate=(1, 1), activation=None, use_bias=True, description: str = ""):
    x = keras.layers.Input(shape)
    y = keras.layers.Conv2D(filters=filters, kernel_size=kernel_size, strides=strides, padding=padding, data_format=data_format,
                            dilation_rate=dilation_rate, activation=activation, use_bias=use_bias)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, *shape).astype(np.float32)
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2, use_tensorflow_converter=False).convert(model)

    generate_kernel_test_case(
        description=f"[keras] Conv2D {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},

        # TODO: replace computation algorithm with more accurate one
        EPS=1e-2
    )


def test():
    template()


def test_kernel_size():
    template(kernel_size=2)


def test_strides():
    template(strides=(2, 2))


def test_padding():
    template(padding="same")


def test_data_format():
    template(shape=(4, 14, 15), data_format="channels_first")


def test_dilation():
    template(shape=(14, 14, 4), dilation_rate=(2, 2))


def test_activation():
    template(activation="relu")


def test_nobias():
    template(use_bias=False)


def test_no_cover_all():
    template(kernel_size=2, shape=(2, 2, 5), strides=2, padding="SAME")
