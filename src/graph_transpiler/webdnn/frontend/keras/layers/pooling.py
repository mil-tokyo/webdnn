import keras

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.frontend.tensorflow.util import check_data_format, parse_padding, convert_odd_padding_to_concat
from webdnn.graph.axis import Axis
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.order import OrderNC, OrderNHWC, OrderNTC
from webdnn.util import console
from webdnn.util.misc import mul


@KerasConverter.register_handler("AveragePooling1D")
def _convert_average_pooling1d(converter: KerasConverter, k_op: "keras.layers.AveragePooling1D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    y = x.reshape([x.shape[0], x.shape[1], 1, x.shape[2]], OrderNHWC)
    ksize = (k_op.pool_size[0], 1)
    stride = (k_op.strides[0], 1)
    padding = (parse_padding(k_op.padding, ksize[0], 1)[0], 0)
    divide_without_padding = padding > 0

    y, = AveragePooling2D(None, ksize=ksize, stride=stride, padding=padding,
                          divide_without_padding=divide_without_padding)(y)
    z = y.reshape([y.shape[0], y.shape[1], y.shape[3]], OrderNTC)

    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("AveragePooling2D")
def _convert_max_pooling2d(converter: KerasConverter, k_op: "keras.layers.AveragePooling2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    check_data_format(x, k_op.data_format)

    padding = (
        parse_padding(k_op.padding, k_op.pool_size[0], 1),
        parse_padding(k_op.padding, k_op.pool_size[1], 1)
    )
    x, padding = convert_odd_padding_to_concat(x, padding=padding)

    divide_without_padding = any(p > 0 for p in padding)
    # handling tensorflow style padding https://github.com/mil-tokyo/webdnn/issues/694

    y, = AveragePooling2D(None, ksize=k_op.pool_size, stride=k_op.strides, padding=padding, cover_all=False,
                          divide_without_padding=divide_without_padding)(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("AveragePooling3D")
def _convert_average_pooling3d(converter: KerasConverter, k_op: "keras.layers.AveragePooling3D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.AveragePooling3D is not supported')


@KerasConverter.register_handler("GlobalMaxPooling1D")
def _convert_global_max_pooling1d(converter: KerasConverter, k_op: "keras.layers.GlobalMaxPooling1D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    y = x.reshape([x.shape[0], x.shape[1], 1, x.shape[2]], OrderNHWC)
    y, = MaxPooling2D(None, ksize=(x.shape[1], 1), stride=(1, 1), padding=(0, 0))(y)

    # flatten without changing memory layout
    z = y.reshape([y.shape[0], mul(y.shape[1:])], OrderNC)
    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("GlobalMaxPooling2D")
def _convert_global_max_pooling2d(converter: KerasConverter, k_op: "keras.layers.GlobalMaxPooling2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    check_data_format(x, k_op.data_format)

    y, = MaxPooling2D(None, ksize=(x.shape_dict[Axis.H], x.shape_dict[Axis.W]), stride=(1, 1), padding=(0, 0))(x)

    # flatten without changing memory layout
    z = y.reshape([y.shape[0], mul(y.shape[1:])], OrderNC)
    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("GlobalAveragePooling1D")
def _convert_global_average_pooling1d(converter: KerasConverter, k_op: "keras.layers.GlobalAveragePooling1D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    y = x.reshape([x.shape[0], x.shape[1], 1, x.shape[2]], OrderNHWC)
    y, = AveragePooling2D(None, ksize=(x.shape[1], 1), stride=(1, 1), padding=(0, 0))(y)

    # flatten without changing memory layout
    z = y.reshape([y.shape[0], mul(y.shape[1:])], OrderNC)
    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("GlobalAveragePooling2D")
def convert_layer_global_average_pooling2d(converter: KerasConverter, k_op: "keras.layers.GlobalAveragePooling2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    check_data_format(x, k_op.data_format)

    y, = AveragePooling2D(None, ksize=(x.shape_dict[Axis.H], x.shape_dict[Axis.W]), stride=(1, 1), padding=(0, 0))(x)

    # flatten without changing memory layout
    z = y.reshape([y.shape[0], mul(y.shape[1:])], OrderNC)
    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("MaxPooling1D")
def _convert_max_pooling1d(converter: KerasConverter, k_op: "keras.layers.MaxPooling1D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    y = x.reshape([x.shape[0], x.shape[1], 1, x.shape[2]], OrderNHWC)
    ksize = (k_op.pool_size[0], 1)
    stride = (k_op.strides[0], 1)
    padding = (parse_padding(k_op.padding, ksize[0], 1)[0], 0)

    y, = MaxPooling2D(None, ksize=ksize, stride=stride, padding=padding)(y)
    z = y.reshape([y.shape[0], y.shape[1], y.shape[3]], OrderNTC)

    converter.set_variable(converter.get_output_tensor(k_op)[0], z)


@KerasConverter.register_handler("MaxPooling2D")
def _convert_max_pooling2d(converter: KerasConverter, k_op: "keras.layers.MaxPooling2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    check_data_format(x, k_op.data_format)

    padding = (
        parse_padding(k_op.padding, k_op.pool_size[0], 1),
        parse_padding(k_op.padding, k_op.pool_size[1], 1)
    )
    x, padding = convert_odd_padding_to_concat(x, padding=padding, value=-1.0e10)

    y, = MaxPooling2D(None, ksize=k_op.pool_size, stride=k_op.strides, padding=padding, cover_all=False)(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("MaxPooling3D")
def _convert_max_pooling3d(converter: KerasConverter, k_op: "keras.layers.MaxPooling3D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.MaxPooling3D is not supported')
