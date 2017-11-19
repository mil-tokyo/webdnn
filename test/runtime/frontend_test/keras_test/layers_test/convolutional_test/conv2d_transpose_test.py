import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.order import OrderNHWC, OrderNCHW


@wrap_template
def template(N=2, H=14, W=15, C1=16, C2=17, ksize=3, strides=(1, 1), padding='valid', data_format=None, dilation=(1, 1),
             activation=None,
             use_bias=True, description: str = ""):
    x = keras.layers.Input((H, W, C1))
    y = keras.layers.Conv2DTranspose(filters=C2, kernel_size=ksize, strides=strides, padding=padding, data_format=data_format,
                                     dilation_rate=dilation, activation=activation, use_bias=use_bias)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(N, H, W, C1).astype(np.float32)
    vy = model.predict(vx, batch_size=N)

    graph = KerasConverter(batch_size=N).convert(model, input_orders=[OrderNCHW if data_format == "channels_first" else OrderNHWC])

    generate_kernel_test_case(
        description=f"[keras] Conv2DTranspose {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},

        # TODO: replace computation algorithm with more accurate one
        EPS=1e-2
    )


def test():
    template()


def test_kernel_size():
    template(ksize=2)


def test_strides():
    template(strides=(2, 2))


def test_padding():
    template(padding="same")


# FIXME: Not supported yet
# def test_data_format():
#     template(data_format="channels_first")

def test_dilation():
    template(dilation=(2, 2))


def test_activation():
    template(activation="relu")


def test_nobias():
    template(use_bias=False)
