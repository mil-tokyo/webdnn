try:
    import keras
except ImportError as e:
    pass

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.axis import Axis
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.order import OrderNC, OrderNCHW, OrderNHWC, OrderNTC
from webdnn.util.misc import mul
from webdnn.util import console


@KerasConverter.register_handler("MaxPooling1D")
def _convert_max_pooling1d(converter: KerasConverter, k_op: "keras.layers.MaxPooling1D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    # FIXME: More effective implementation
    y, = Reshape(None, in_order=x.order, out_order=OrderNHWC, out_shape=[x.shape[0], x.shape[1], 1, x.shape[2]])(x)

    if k_op.padding == "valid":
        padding = (0, 0)

    elif k_op.padding == "same":
        padding = (k_op.pool_size[0] // 2, 0)

    else:
        raise NotImplementedError(f"Unknown padding: {k_op.padding}")

    y, = MaxPooling2D(None, ksize=(k_op.pool_size[0], 1), stride=(1, 1), padding=padding)(y)
    z, = Reshape(None, in_order=y.order, out_order=OrderNTC, out_shape=[y.shape[0], y.shape[1], y.shape[3]])(y)

    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("MaxPooling2D")
def _convert_max_pooling2d(converter: KerasConverter, k_op: "keras.layers.MaxPooling2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    if k_op.data_format == "channels_first":
        assert x.order == OrderNCHW

    elif k_op.data_format == "channels_last":
        assert x.order == OrderNHWC

    else:
        raise ValueError(f"[KerasConverter] Unknown data format: {k_op.data_format}")

    ksize = tuple(k_op.pool_size)
    stride = tuple(k_op.strides)
    if k_op.padding == "valid":
        padding = (0, 0)

    elif k_op.padding == "same":
        padding = (ksize[0] // 2, ksize[1] // 2)

    else:
        raise ValueError(f"[KerasConverter] Unknown padding: {k_op.padding}")

    y, = MaxPooling2D(None, ksize=ksize, stride=stride, padding=padding)(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("MaxPooling3D")
def _convert_max_pooling3d(converter: KerasConverter, k_op: "keras.layers.MaxPooling3D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.MaxPooling3D is not supported')


@KerasConverter.register_handler("AveragePooling1D")
def _convert_average_pooling1d(converter: KerasConverter, k_op: "keras.layers.AveragePooling1D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    # FIXME: More effective implementation
    y, = Reshape(None, in_order=x.order, out_order=OrderNHWC, out_shape=[x.shape[0], x.shape[1], 1, x.shape[2]])(x)

    if k_op.padding == "valid":
        padding = (0, 0)

    elif k_op.padding == "same":
        padding = (k_op.pool_size[0] // 2, 0)

    else:
        raise NotImplementedError(f"Unknown padding: {k_op.padding}")

    y, = AveragePooling2D(None, ksize=(k_op.pool_size[0], 1), stride=(1, 1), padding=padding)(y)
    z, = Reshape(None, in_order=y.order, out_order=OrderNTC, out_shape=[y.shape[0], y.shape[1], y.shape[3]])(y)

    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("AveragePooling2D")
def _convert_max_pooling2d(converter: KerasConverter, k_op: "keras.layers.AveragePooling2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    if k_op.data_format == "channels_first":
        assert x.order == OrderNCHW

    elif k_op.data_format == "channels_last":
        assert x.order == OrderNHWC

    else:
        raise ValueError(f"[KerasConverter] Unknown data format: {k_op.data_format}")

    ksize = tuple(k_op.pool_size)
    stride = tuple(k_op.strides)
    if k_op.padding == "valid":
        padding = (0, 0)

    elif k_op.padding == "same":
        padding = (ksize[0] // 2, ksize[1] // 2)
        console.warning(
            "[KerasConverter] keras.layers.AveragePooling with padding divides summed values in window by the number "
            "of valid elements, but WebDNN divides it by the number of elements including zero padding, so different "
            "result will be generated on the edge.")

    else:
        raise ValueError(f"[KerasConverter] Unknown padding: {k_op.padding}")

    y, = AveragePooling2D(None, ksize=ksize, stride=stride, padding=padding)(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("AveragePooling3D")
def _convert_average_pooling3d(converter: KerasConverter, k_op: "keras.layers.AveragePooling3D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.AveragePooling3D is not supported')


@KerasConverter.register_handler("GlobalMaxPooling1D")
def _convert_global_max_pooling1d(converter: KerasConverter, k_op: "keras.layers.GlobalMaxPooling1D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    # FIXME: More effective implementation
    y, = Reshape(None, in_order=OrderNTC, out_order=OrderNHWC, out_shape=[x.shape[0], x.shape[1], 1, x.shape[2]])(x)
    y, = MaxPooling2D(None, ksize=(x.shape[1], 1), stride=(1, 1), padding=(0, 0))(y)

    # flatten without changing memory layout
    z, = Reshape(None, in_order=y.order, out_order=OrderNC, out_shape=[y.shape[0], mul(y.shape[1:])])(y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("GlobalMaxPooling2D")
def _convert_global_max_pooling2d(converter: KerasConverter, k_op: "keras.layers.GlobalMaxPooling2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    if k_op.data_format == "channels_first":
        assert x.order == OrderNCHW

    elif k_op.data_format == "channels_last":
        assert x.order == OrderNHWC

    else:
        raise ValueError(f"[KerasConverter] Unknown data format: {k_op.data_format}")

    y, = MaxPooling2D(None, ksize=(x.shape_dict[Axis.H], x.shape_dict[Axis.W]), stride=(1, 1), padding=(0, 0))(x)

    # flatten without changing memory layout
    z, = Reshape(None, in_order=y.order, out_order=OrderNC, out_shape=[y.shape[0], mul(y.shape[1:])])(y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("GlobalAveragePooling1D")
def _convert_global_average_pooling1d(converter: KerasConverter, k_op: "keras.layers.GlobalAveragePooling1D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    # FIXME: More effective implementation
    y, = Reshape(None, in_order=OrderNTC, out_order=OrderNHWC, out_shape=[x.shape[0], x.shape[1], 1, x.shape[2]])(x)
    y, = AveragePooling2D(None, ksize=(x.shape[1], 1), stride=(1, 1), padding=(0, 0))(y)

    # flatten without changing memory layout
    z, = Reshape(None, in_order=y.order, out_order=OrderNC, out_shape=[y.shape[0], mul(y.shape[1:])])(y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("GlobalAveragePooling2D")
def convert_layer_global_average_pooling2d(converter: KerasConverter, k_op: "keras.layers.GlobalAveragePooling2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    if k_op.data_format == "channels_first":
        assert x.order == OrderNCHW

    elif k_op.data_format == "channels_last":
        assert x.order == OrderNHWC

    else:
        raise ValueError(f"[KerasConverter] Unknown data format: {k_op.data_format}")

    y, = AveragePooling2D(None, ksize=(x.shape_dict[Axis.H], x.shape_dict[Axis.W]), stride=(1, 1), padding=(0, 0))(x)

    # flatten without changing memory layout
    z, = Reshape(None, in_order=y.order, out_order=OrderNC, out_shape=[y.shape[0], mul(y.shape[1:])])(y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], z)
