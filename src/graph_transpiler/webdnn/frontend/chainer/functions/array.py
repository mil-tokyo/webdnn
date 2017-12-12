from itertools import combinations

import chainer
import numpy as np
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
from webdnn.util.misc import mul


# TODO: Broadcast

@ChainerConverter.register_handler("BroadcastTo")
def _convert_broadcast_to(converter: ChainerConverter, c_op: "chainer.functions.BroadcastTo"):
    x = converter.get_variable(c_op.inputs[0])
    # noinspection PyProtectedMember
    y, = Broadcast(None, out_shape=c_op._shape, out_order=x.order)(x)
    converter.set_variable(c_op.outputs[0](), y)


# TODO: Cast

@ChainerConverter.register_handler("Concat")
def _convert_concat(converter: ChainerConverter, c_op: "chainer.functions.Concat"):
    xs = [converter.get_variable(x) for x in c_op.inputs]

    for x1, x2 in combinations(xs, 2):
        x1.order.unify(x2.order)

    y, = Concat(None, axis=xs[0].order.axes[c_op.axis])(*xs)
    converter.set_variable(c_op.outputs[0](), y)


# TODO: Copy

@ChainerConverter.register_handler("Depth2Space")
def _convert_depth2space(converter: ChainerConverter, c_op: "chainer.functions.Depth2Space"):
    x = converter.get_variable(c_op.inputs[0])
    x.order.unify(OrderNCHW)
    y, = Depth2Space(None, r=c_op.r)(x)
    converter.set_variable(c_op.outputs[0](), y)


# TODO: Dstack

@ChainerConverter.register_handler("ExpandDims")
def _convert_expand_dims(converter: ChainerConverter, c_op: "chainer.functions.ExpandDims"):
    x = converter.get_variable(c_op.inputs[0])
    y = x.expand_dims(Axis(), c_op.axis)
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Flatten")
def _convert_flatten(converter: ChainerConverter, c_op: "chainer.functions.Flatten"):
    x = converter.get_variable(c_op.inputs[0])
    y = x.reshape([x.size], Order([None]))
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("FlipLR")
def _convert_flip_lr(converter: ChainerConverter, c_op: "chainer.functions.FlipLR"):
    x = converter.get_variable(c_op.inputs[0])
    converter.set_variable(c_op.outputs[0](), x[:, ::-1])


@ChainerConverter.register_handler("FlipUD")
def _convert_flip_ud(converter: ChainerConverter, c_op: "chainer.functions.FlipUD"):
    x = converter.get_variable(c_op.inputs[0])
    converter.set_variable(c_op.outputs[0](), x[::-1, :])


@ChainerConverter.register_handler("GetItem")
def _convert_get_item(converter: ChainerConverter, c_op: "chainer.functions.GetItem"):
    x = converter.get_variable(c_op.inputs[0])
    y = x[c_op.slices]
    converter.set_variable(c_op.outputs[0](), y)


# TODO: HStack

@ChainerConverter.register_handler("Im2Col")
def _convert_im2col(converter: ChainerConverter, c_op: "chainer.functions.Im2Col"):
    x = converter.get_variable(c_op.inputs[0])
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


# TODO: Pad

# TODO: PadSequence

# TODO: Permutate

@ChainerConverter.register_handler("Reshape")
def _convert_reshape(converter: ChainerConverter, c_op: "chainer.functions.Reshape"):
    x = converter.get_variable(c_op.inputs[0])

    out_shape = list(c_op.shape)
    out_order = Order([None] * len(out_shape))
    if -1 in out_shape:
        i = out_shape.index(-1)
        out_shape.pop(i)
        out_shape.insert(i, x.size // mul(out_shape))

    assert mul(out_shape) == x.size, f"[ChainerConverter] Shape mismatch: mul(out_shape)={mul(out_shape)}, x.size={x.size}"

    y = x.reshape(out_shape, out_order)

    converter.set_variable(c_op.outputs[0](), y)


# TODO: ResizeImages

# TODO: Rollaxis

# TODO: SelectItem

@ChainerConverter.register_handler("Space2Depth")
def _convert_space2depth(converter: ChainerConverter, c_op: "chainer.functions.Space2Depth"):
    x = converter.get_variable(c_op.inputs[0])
    x.order.unify(OrderNCHW)
    y, = Space2Depth(None, r=c_op.r)(x)
    converter.set_variable(c_op.outputs[0](), y)


# TODO: SpatialTransformerGrid

# TODO: SpatialTransformerSampler

@ChainerConverter.register_handler("SplitAxis")
def _convert_split_axis(converter: ChainerConverter, c_op: "chainer.functions.SplitAxis"):
    x = converter.get_variable(c_op.inputs[0])

    if isinstance(c_op.indices_or_sections, int):
        raise NotImplementedError("[ChainerConverter] SplitAxis with indices are not supported.")

    ys = SplitAxis(None, sections=c_op.indices_or_sections, axis=x.order.axes[c_op.axis])(x)
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


@ChainerConverter.register_handler("Transpose")
def _convert_transpose(converter: ChainerConverter, c_op: "chainer.functions.Transpose"):
    x = converter.get_variable(c_op.inputs[0])
    y = x.transpose(Order([x.order.axes[axis] for axis in c_op.axes]))

    converter.set_variable(c_op.outputs[0](), y)

# TODO: TransposeSequence

# TODO: Where
