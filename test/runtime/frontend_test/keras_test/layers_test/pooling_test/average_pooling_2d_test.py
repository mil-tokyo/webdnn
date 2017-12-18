import numpy as np

from test.runtime.frontend_test.keras_test.util import keras, KerasConverter
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(pool_size=(3, 3), shape=(15, 17, 16), strides=(2, 2), padding="valid", data_format=None, description: str = ""):
    x = keras.layers.Input(shape)
    y = keras.layers.AveragePooling2D(pool_size=pool_size, strides=strides, padding=padding, data_format=data_format)(x)
    model = keras.models.Model([x], [y])

    vx = np.random.rand(2, *shape)
    vy = model.predict(vx, batch_size=2)

    graph = KerasConverter(batch_size=2, use_tensorflow_converter=False).convert(model)
    assert list(vy.shape) == list(graph.outputs[0].shape), f"(vy.shape)={vy.shape}, (graph.outputs[0].shape)={graph.outputs[0].shape}"

    generate_kernel_test_case(
        description=f"[keras] AveragePooling2D {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_irregular_size():
    template(pool_size=(3, 4), strides=(2, 1))


def test_channels_first():
    template(data_format="channels_first")


def test_padding_valid():
    template(padding="valid")


# FIXME: Not supported yet
# def test_padding_same():
#     template(padding="same")


def test_no_cover_all():
    template(pool_size=2, shape=(2, 2, 5), strides=2, padding="SAME")
