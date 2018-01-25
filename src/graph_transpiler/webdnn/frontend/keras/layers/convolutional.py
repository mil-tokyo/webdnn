import keras

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.frontend.keras.layers.util import do_activation
from webdnn.frontend.tensorflow.util import check_data_format, parse_padding, convert_odd_padding_to_concat
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.slice import Slice
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.operators.zero_padding_1d import ZeroPadding1D
from webdnn.graph.operators.zero_padding_2d import ZeroPadding2D
from webdnn.graph.order import OrderC, OrderNTC, Order, OrderNHWC, OrderNCHW


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Conv1D")
def _convert_conv1d(converter: KerasConverter, k_op: "keras.layers.Conv1D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Conv1D is not supported')


@KerasConverter.register_handler("Conv2D")
def _convert_conv2d(converter: KerasConverter, k_op: "keras.layers.Conv2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    check_data_format(x, k_op.data_format)

    w = converter.convert_to_constant_variable(k_op.kernel, Order([Axis.KH, Axis.KW, Axis.C, Axis.N]))

    padding = (
        parse_padding(k_op.padding, k_op.kernel_size[0], k_op.dilation_rate[0]),
        parse_padding(k_op.padding, k_op.kernel_size[1], k_op.dilation_rate[1])
    )
    x, padding = convert_odd_padding_to_concat(x, padding=padding)
    y, = Convolution2D(None, ksize=k_op.kernel_size, stride=k_op.strides, padding=padding, dilation_rate=k_op.dilation_rate)(x, w)

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(k_op.bias, OrderC)
        y = y + b

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("Conv2DTranspose")
def _convert_conv2d_transpose(converter: KerasConverter, k_op: "keras.layers.Conv2DTranspose"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    check_data_format(x, k_op.data_format)

    w = converter.convert_to_constant_variable(k_op.kernel, Order([Axis.KH, Axis.KW, Axis.N, Axis.C]))

    if tuple(k_op.dilation_rate) != (1, 1):
        raise NotImplementedError("[KerasConverter] keras.layers.Convolution2DTranspose with large dilation_rate is not supported")

    padding = (
        parse_padding(k_op.padding, k_op.kernel_size[0], k_op.dilation_rate[0]),
        parse_padding(k_op.padding, k_op.kernel_size[1], k_op.dilation_rate[1])
    )

    if any(p[0] != p[1] for p in padding):
        pad_col2im = tuple(p[0] if p[0] == p[1] else 0 for p in padding)
        pad_extra = tuple((0, 0) if p[0] == p[1] else p for p in padding)
        y, = Deconvolution2D(None, ksize=k_op.kernel_size, stride=k_op.strides, padding=pad_col2im)(x, w)

        if k_op.data_format == "channels_first":
            y = y[:, :, pad_extra[0][0]:-pad_extra[0][1], pad_extra[1][0]:-pad_extra[1][1]]

        elif k_op.data_format == "channels_last":
            y = y[:, pad_extra[0][0]:-pad_extra[0][1], pad_extra[1][0]:-pad_extra[1][1], :]

        else:
            raise NotImplementedError(f"Unknown data format: {k_op.data_format}")

    else:
        y, = Deconvolution2D(None, ksize=k_op.kernel_size, stride=k_op.strides, padding=tuple(p[0] for p in padding))(x, w)

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(k_op.bias, OrderC)
        y = y + b

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Conv3D")
def _convert_conv3d(converter: KerasConverter, k_op: "keras.layers.Conv3D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Conv3D is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Cropping1D")
def _convert_cropping1d(converter: KerasConverter, k_op: "keras.layers.Cropping1D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Cropping1D is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Cropping2D")
def _convert_cropping2d(converter: KerasConverter, k_op: "keras.layers.Cropping2D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Cropping2D is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("Cropping3D")
def _convert_cropping3d(converter: KerasConverter, k_op: "keras.layers.Cropping3D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.Cropping3D is not supported')


@KerasConverter.register_handler("SeparableConv2D")
def _convert_separable_conv2d(converter: KerasConverter, k_op: "keras.layers.SeparableConv2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    check_data_format(x, k_op.data_format)
    axis_c_in = Axis.C
    axis_c_out = Axis()
    axis_depth_multiplier = Axis()

    w_depthwise = converter.convert_to_constant_variable(k_op.depthwise_kernel, Order([Axis.KH, Axis.KW, axis_c_in, axis_depth_multiplier]))

    w_pointwise = converter.convert_to_constant_variable(k_op.pointwise_kernel, Order([Axis.KH, Axis.KW, axis_c_in, axis_c_out]))
    w_pointwise = w_pointwise.reshape(shape=[x.shape_dict[axis_c_in], k_op.depth_multiplier, w_pointwise.shape_dict[axis_c_out]],
                                      order=Order([axis_c_in, axis_depth_multiplier, axis_c_out]))

    ksize = tuple(k_op.kernel_size)
    stride = tuple(k_op.strides)
    dilation_rate = tuple(k_op.dilation_rate)
    padding = (parse_padding(k_op.padding, ksize[0], dilation_rate[0]), parse_padding(k_op.padding, ksize[1], dilation_rate[1]))
    if any(p[0] != p[1] for p in padding):
        raise NotImplementedError("[KerasConverter] \"Different size padding\" is not supported yet")
    padding = tuple(p[0] for p in padding)

    h, = Im2Col(None, ksize=ksize, stride=stride, padding=padding, dilation_rate=dilation_rate)(x)

    # TODO: Support depth-wise convolution natively
    # Currently, depth-wise convolution is not supported natively, and emulated by composition of small convolution operations.
    ys = []
    for i in range(h.shape_dict[axis_c_in]):
        # 1. Depthwise convolution
        #
        # Ideal                             | Current implementation
        # ----------------------------------+----------------------------------------------------
        # h.axes=[N, H, W, KH, KW, C_in]    | g_sub.axes=[N, H, W, KH, KW]
        # w.axes=[KH, KW, C_in, DM]         | w_sub.axes=[KH, KW, DM]
        # g.axes=[N, H, W, C_in, DM]        | g_sub.axes=[N, H, W, DM]

        h_sub, = Slice(None, indices=AxisKeyDict(h.order.axes, [i if a == axis_c_in else slice(None) for a in h.order.axes]))(h)
        w_depthwise_sub = w_depthwise[:, :, i, :]
        g_sub, = Tensordot(None, axes=((Axis.KH, Axis.KW), (Axis.KH, Axis.KW)))(h_sub, w_depthwise_sub)

        # 2. Pointwise (projection) convolution
        #
        # Ideal                             | Current implementation
        # ----------------------------------+----------------------------------------------------
        # g.axes=[N, H, W, C_in, DM]        | g_sub.axes=[N, H, W, DM]
        # w.axes=[DM, Cin, C_out]           | w_sub.axes=[DM, C_out]
        # y.axes=[N, H, W, C_out]           | y_sub.axes=[N, H, W, C_out]

        w_pointwise_sub = w_pointwise[i, :, :]
        y_sub, = Tensordot(None, axes=((axis_depth_multiplier,), (axis_depth_multiplier,)))(g_sub, w_pointwise_sub)
        ys.append(y_sub)

    # Sum up all sub convolution results to one
    while len(ys) > 1:
        ys.append(ys.pop(0) + ys.pop(0))

    y = ys[0]

    # reinterpret axis "C_out" as C
    axes = list(y.order.axes)
    i = axes.index(axis_c_out)
    axes.pop(i)
    axes.insert(i, Axis.C)
    y = y.reinterpret_axes(Order(axes))

    if k_op.data_format == "channels_last":
        y = y.transpose(OrderNHWC)

    elif k_op.data_format == "channels_first":
        y = y.transpose(OrderNCHW)

    else:
        raise NotImplementedError(f"[KerasConverter] Unknown data format: {k_op.data_format}")

    if k_op.use_bias:
        b = converter.convert_to_constant_variable(k_op.bias, OrderC)
        y = y + b

    y = do_activation(k_op.activation, y)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("UpSampling1D")
def _convert_up_sampling1d(converter: KerasConverter, k_op: "keras.layers.UpSampling1D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.UpSampling1D is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("UpSampling2D")
def _convert_up_sampling2d(converter: KerasConverter, k_op: "keras.layers.UpSampling2D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.UpSampling2D is not supported')


# noinspection PyUnusedLocal
@KerasConverter.register_handler("UpSampling3D")
def _convert_up_sampling2d(converter: KerasConverter, k_op: "keras.layers.UpSampling3D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.UpSampling3D is not supported')


@KerasConverter.register_handler("ZeroPadding1D")
def _convert_zero_padding1d(converter: KerasConverter, k_op: "keras.layers.ZeroPadding1D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    x.order.unify(OrderNTC)

    y, = ZeroPadding1D(None, padding=tuple(k_op.padding))(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


@KerasConverter.register_handler("ZeroPadding2D")
def _convert_zero_padding2d(converter: KerasConverter, k_op: "keras.layers.ZeroPadding2D"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])
    check_data_format(x, k_op.data_format)

    padding = k_op.padding
    top = padding[0][0]
    if top != padding[0][1]:
        # FIXME: This condition should be checked in each backend
        raise NotImplementedError(
            "[KerasConverter] In current implementation, Padding size of top and bottom must be same.")

    left = padding[1][0]
    if left != padding[1][1]:
        # FIXME: This condition should be checked in each backend
        raise NotImplementedError(
            "[KerasConverter] In current implementation, Padding size of left and right must be same.")

    y, = ZeroPadding2D(None, (top, left))(x)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("ZeroPadding3D")
def _convert_zero_padding3d(converter: KerasConverter, k_op: "keras.layers.ZeroPadding3D"):
    # TODO
    raise NotImplementedError('[KerasConverter] keras.layers.ZeroPadding3D is not supported')
