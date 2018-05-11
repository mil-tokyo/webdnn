from itertools import combinations

import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operators.broadcast import Broadcast
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.space2depth import Space2Depth
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.operators.tile import Tile
from webdnn.graph.order import Order
from webdnn.graph.order import OrderNCHW
from webdnn.graph.placeholder import Placeholder
from webdnn.util.misc import mul
from webdnn.frontend.util import semver


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Broadcast")
def _convert_broadcast(converter: ChainerConverter, c_op: "chainer.functions.Broadcast"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Broadcast is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("BroadcastTo")
def _convert_broadcast_to(converter: ChainerConverter, c_op: "chainer.functions.BroadcastTo"):
    x = converter.get_variable(c_op.inputs[0])
    if any(not Placeholder.check_resolved(v) for v in x.shape):
        raise NotImplementedError("[ChainerConverter] \"BroadcastTo\" for dynamic shape variable is not supported ")

    # noinspection PyProtectedMember
    y, = Broadcast(None, out_shape=c_op._shape, out_order=x.order)(x)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Cast")
def _convert_cast(converter: ChainerConverter, c_op: "chainer.functions.Cast"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Cast is not supported")


@ChainerConverter.register_handler("Concat")
def _convert_concat(converter: ChainerConverter, c_op: "chainer.functions.Concat"):
    xs = [converter.get_variable(x) for x in c_op.inputs]

    for x1, x2 in combinations(xs, 2):
        x1.order.unify(x2.order)

    y, = Concat(None, axis=xs[0].order.axes[c_op.axis])(*xs)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Copy")
def _convert_copy(converter: ChainerConverter, c_op: "chainer.functions.Copy"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Copy is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Depth2Space")
def _convert_depth2space(converter: ChainerConverter, c_op: "chainer.functions.Depth2Space"):
    x = converter.get_variable(c_op.inputs[0])
    x.order.unify(OrderNCHW)
    y, = Depth2Space(None, r=c_op.r)(x)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal,PyUnresolvedReferences
@ChainerConverter.register_handler("Dstack")
def _convert_dstack(converter: ChainerConverter, c_op: "chainer.functions.array.dstack.Dstack"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Dstack is not supported")


@ChainerConverter.register_handler("ExpandDims")
def _convert_expand_dims(converter: ChainerConverter, c_op: "chainer.functions.ExpandDims"):
    x = converter.get_variable(c_op.inputs[0])
    y = x.expand_dims(Axis(), c_op.axis)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("Flatten")
def _convert_flatten(converter: ChainerConverter, c_op: "chainer.functions.Flatten"):
    x = converter.get_variable(c_op.inputs[0])
    y = x.reshape([x.size], Order([None]))
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("FlipLR")
def _convert_flip_lr(converter: ChainerConverter, c_op: "chainer.functions.FlipLR"):
    x = converter.get_variable(c_op.inputs[0])
    if any(not Placeholder.check_resolved(v) for v in x.shape):
        raise NotImplementedError("[ChainerConverter] \"FlipLR\" for dynamic shape variable is not supported ")

    converter.set_variable(c_op.outputs[0](), x[:, ::-1])


@ChainerConverter.register_handler("FlipUD")
def _convert_flip_ud(converter: ChainerConverter, c_op: "chainer.functions.FlipUD"):
    x = converter.get_variable(c_op.inputs[0])
    if any(not Placeholder.check_resolved(v) for v in x.shape):
        raise NotImplementedError("[ChainerConverter] \"FlipUD\" for dynamic shape variable is not supported ")

    converter.set_variable(c_op.outputs[0](), x[::-1, :])


@ChainerConverter.register_handler("GetItem")
def _convert_get_item(converter: ChainerConverter, c_op: "chainer.functions.GetItem"):
    x = converter.get_variable(c_op.inputs[0])
    if any(not Placeholder.check_resolved(v) for v in x.shape):
        raise NotImplementedError("[ChainerConverter] \"GetItem\" for dynamic shape variable is not supported ")

    y = x[c_op.slices]
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal,PyUnresolvedReferences
@ChainerConverter.register_handler("Hstack")
def _convert_hstack(converter: ChainerConverter, c_op: "chainer.functions.array.hstack.Hstack"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Hstack is not supported")


@ChainerConverter.register_handler("Im2Col")
def _convert_im2col(converter: ChainerConverter, c_op: "chainer.functions.Im2Col"):
    x = converter.get_variable(c_op.inputs[0])
    if any(not Placeholder.check_resolved(v) for v in x.shape):
        raise NotImplementedError("[ChainerConverter] \"GetItem\" for dynamic shape variable is not supported ")

    x.order.unify(OrderNCHW)
    if c_op.cover_all:
        raise NotImplementedError("[ChainerConverter] \"Im2Col\" function with \"cover_all=True\" is not supported")

    y, = Im2Col(None,
                ksize=(c_op.kh, c_op.kw),
                stride=(c_op.sy, c_op.sx),
                padding=(c_op.ph, c_op.pw),
                dilation_rate=(c_op.dy, c_op.dx))(x)

    y = y.combine_axes([Axis.C, Axis.KH, Axis.KW], Axis.C).change_order(OrderNCHW)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Pad")
def _convert_pad(converter: ChainerConverter, c_op: "chainer.functions.Pad"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Pad is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("PadSequence")
def _convert_pad_sequence(converter: ChainerConverter, c_op: "chainer.functions.PadSequence"):
    # TODO
    raise NotImplementedError("[ChainerConverter] PadSequence is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Permutate")
def _convert_permutate(converter: ChainerConverter, c_op: "chainer.functions.Permutate"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Permutate is not supported")


@ChainerConverter.register_handler("Reshape")
def _convert_reshape(converter: ChainerConverter, c_op: "chainer.functions.Reshape"):
    x = converter.get_variable(c_op.inputs[0])
    if any(not Placeholder.check_resolved(v) for v in x.shape):
        raise NotImplementedError("[ChainerConverter] \"Reshape\" for dynamic shape variable is not supported ")

    out_shape = list(c_op.shape)
    out_order = Order([None] * len(out_shape))
    if -1 in out_shape:
        i = out_shape.index(-1)
        out_shape.pop(i)
        out_shape.insert(i, x.size // mul(out_shape))

    assert mul(out_shape) == x.size, f"[ChainerConverter] Shape mismatch: mul(out_shape)={mul(out_shape)}, x.size={x.size}"

    y = x.reshape(out_shape, out_order)

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("ResizeImages")
def _convert_resize_images(converter: ChainerConverter, c_op: "chainer.functions.ResizeImages"):
    # TODO
    raise NotImplementedError("[ChainerConverter] ResizeImages is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Rollaxis")
def _convert_rollaxis(converter: ChainerConverter, c_op: "chainer.functions.Rollaxis"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Rollaxis is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("SelectItem")
def _convert_selected_item(converter: ChainerConverter, c_op: "chainer.functions.SelectItem"):
    # TODO
    raise NotImplementedError("[ChainerConverter] SelectItem is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Space2Depth")
def _convert_space2depth(converter: ChainerConverter, c_op: "chainer.functions.Space2Depth"):
    x = converter.get_variable(c_op.inputs[0])
    x.order.unify(OrderNCHW)
    y, = Space2Depth(None, r=c_op.r)(x)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("SpatialTransformerGrid")
def _convert_spatial_transformer_grid(converter: ChainerConverter, c_op: "chainer.functions.SpatialTransformerGrid"):
    # TODO
    raise NotImplementedError("[ChainerConverter] SpatialTransformerGrid is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("SpatialTransformerSampler")
def _convert_spatial_transformer_sampler(converter: ChainerConverter,
                                         c_op: "chainer.functions.SpatialTransformerSampler"):
    # TODO
    raise NotImplementedError("[ChainerConverter] SpatialTransformerSampler is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("SplitAxis")
def _convert_split_axis(converter: ChainerConverter, c_op: "chainer.functions.SplitAxis"):
    x = converter.get_variable(c_op.inputs[0])

    VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = semver(chainer.__version__)
    if VERSION_MAJOR >= 4:
        # Internal data structure changed
        # https://github.com/chainer/chainer/commit/906a8e9b0837cd9a4e5ee6f1dbda26431a1e12d1#diff-9e610d281c820d44c4a0cbf0ca6263fd
        if c_op.indices is None:
            raise NotImplementedError("[ChainerConverter] SplitAxis with sections are not supported.")
        indices = c_op.indices
    else:
        if isinstance(c_op.indices_or_sections, int):
            raise NotImplementedError("[ChainerConverter] SplitAxis with sections are not supported.")
        indices = c_op.indices_or_sections

    ys = SplitAxis(None, sections=indices, axis=x.order.axes[c_op.axis])(x)
    for i, y in enumerate(ys):
        converter.set_variable(c_op.outputs[i](), y)


@ChainerConverter.register_handler("Squeeze")
def _convert_squeeze(converter: ChainerConverter, c_op: "chainer.functions.Squeeze"):
    x = converter.get_variable(c_op.inputs[0])
    if c_op.axis is None:
        axes = [a for a in x.order.axes if x.shape_dict[a] == 1]
    else:
        axes = [x.order.axes[i] for i in c_op.axis]

    for axis in axes:
        x = x.squeeze(axis)

    converter.set_variable(c_op.outputs[0](), x)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Swapaxes")
def _convert_swapaxes(converter: ChainerConverter, c_op: "chainer.functions.Swapaxes"):
    x = converter.get_variable(c_op.inputs[0])
    index = list(range(x.ndim))
    index[c_op.axis1] = c_op.axis2
    index[c_op.axis2] = c_op.axis1
    y = x.transpose(Order([x.order.axes[i] for i in index]))

    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Tile")
def _convert_tile(converter: ChainerConverter, c_op: "chainer.functions.Tile"):
    x = converter.get_variable(c_op.inputs[0])
    reps = c_op.reps

    if x.ndim > len(reps):
        reps = (1,) * (x.ndim - len(reps)) + reps

    else:
        while x.ndim < len(c_op.reps):
            x = x.expand_dims(Axis(), 0)

    y, = Tile(None, AxisKeyDict(x.order.axes, reps))(x)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Transpose")
def _convert_transpose(converter: ChainerConverter, c_op: "chainer.functions.Transpose"):
    x = converter.get_variable(c_op.inputs[0])
    y = x.transpose(Order([x.order.axes[axis] for axis in c_op.axes]))

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("TransposeSequence")
def _convert_transpose_sequence(converter: ChainerConverter, c_op: "chainer.functions.TransposeSequence"):
    # TODO
    raise NotImplementedError("[ChainerConverter] TransposeSequence is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Where")
def _convert_where(converter: ChainerConverter, c_op: "chainer.functions.Where"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Where is not supported")
