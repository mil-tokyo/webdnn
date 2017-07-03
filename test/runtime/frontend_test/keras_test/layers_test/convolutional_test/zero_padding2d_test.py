from unittest import SkipTest


def test():
    raise SkipTest  # FIXME: ZeroPadding2D is supported only when it's used with convolution or pooling.from

    # for kwargs in [
    #     {"padding": (0, 0)},
    #     {"padding": (1, 1)},
    #     # {"padding": ((1, 2), (3, 4))}, # FIXME: Not Supported Yet
    #     {"padding": (1, 1), "data_format": "channels_first"},
    #     {"padding": (1, 1), "data_format": "channels_last"},
    # ]:
    #     channels_first = ("data_format" in kwargs) and (kwargs["data_format"] == "channels_first")
    #
    #     x = keras.layers.Input((14, 15, 16))
    #     y = keras.layers.ZeroPadding2D(**kwargs)(x)
    #     model = keras.models.Model([x], [y])
    #
    #     vx = np.random.rand(2, 14, 15, 16)
    #     vy = model.predict(vx, batch_size=2)
    #
    #     graph = KerasConverter(batch_size=2).convert(model, input_orders=[OrderNCHW if channels_first else OrderNHWC])
    #
    #     generate_kernel_test_case(
    #         description="[keras] ZeroPadding2D " + (", ".join([f"{k}={v}" for k, v in kwargs.items()])),
    #         graph=graph,
    #         inputs={graph.inputs[0]: vx},
    #         expected={graph.outputs[0]: vy},
    #         raise_skip=False
    #     )
    #
    # raise SkipTest
