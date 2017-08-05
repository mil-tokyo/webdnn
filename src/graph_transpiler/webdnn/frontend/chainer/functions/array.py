from itertools import combinations

import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.constraints import unify_order, AxisVar
from webdnn.graph.operators.broadcast import Broadcast
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.space2depth import Space2Depth
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.order import OrderC, OrderNCHW, Order
from webdnn.util import console
from webdnn.util.misc import mul


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Broadcast")
def _convert_broadcast(converter: ChainerConverter, c_op: "chainer.functions.Broadcast"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Broadcast is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("BroadcastTo")
def _convert_broadcast_to(converter: ChainerConverter, c_op: "chainer.functions.BroadcastTo"):
    x = converter.get_variable(c_op.inputs[0])
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
        unify_order(x1.order, x2.order)

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
    unify_order(x.order, OrderNCHW)
    y, = Depth2Space(None, r=c_op.r)(x)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal,PyUnresolvedReferences
@ChainerConverter.register_handler("Dstack")
def _convert_dstack(converter: ChainerConverter, c_op: "chainer.functions.array.dstack.Dstack"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Dstack is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("ExpandDims")
def _convert_expand_dims(converter: ChainerConverter, c_op: "chainer.functions.ExpandDims"):
    # TODO
    raise NotImplementedError("[ChainerConverter] ExpandDims is not supported")


@ChainerConverter.register_handler("Flatten")
def _convert_flatten(converter: ChainerConverter, c_op: "chainer.functions.Flatten"):
    x = converter.get_variable(c_op.inputs[0])
    y, = Reshape(None, in_order=x.order, out_shape=[x.size], out_order=OrderC)  # FIXME: OrderC
    converter.set_variable(c_op.outputs[0](), y)

    console.warning("[ChainerConverter] In chainer.functions.Flatten, output data order is parsed as OrderC. To "
                    "customize this, please overwrite chainer.functions.Flatten converter handler.")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("FlipLR")
def _convert_flip_lr(converter: ChainerConverter, c_op: "chainer.functions.FlipLR"):
    # TODO
    raise NotImplementedError("[ChainerConverter] FlipLR is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("FlipUD")
def _convert_flip_ud(converter: ChainerConverter, c_op: "chainer.functions.FlipUD"):
    # TODO
    raise NotImplementedError("[ChainerConverter] FlipUD is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("GetItem")
def _convert_get_item(converter: ChainerConverter, c_op: "chainer.functions.GetItem"):
    # TODO
    raise NotImplementedError("[ChainerConverter] GetItem is not supported")


# noinspection PyUnusedLocal,PyUnresolvedReferences
@ChainerConverter.register_handler("Hstack")
def _convert_hstack(converter: ChainerConverter, c_op: "chainer.functions.array.hstack.Hstack"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Hstack is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Im2Col")
def _convert_im2col(converter: ChainerConverter, c_op: "chainer.functions.Im2Col"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Im2Col is not supported")


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

    out_shape = c_op.shape
    # noinspection PyTypeChecker
    out_order = Order([AxisVar() for _ in out_shape])
    assert mul(out_shape) == x.size, f"[ChainerConverter] Shape mismatch: mul(out_shape)={mul(out_shape)}, x.size={x.size}"

    y, = Reshape(None, in_order=x.order, out_order=out_order, out_shape=out_shape)(x)

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
    unify_order(x.order, OrderNCHW)
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

    if isinstance(c_op.indices_or_sections, int):
        raise NotImplementedError("[ChainerConverter] SplitAxis with indices are not supported.")

    ys = SplitAxis(None, sections=c_op.indices_or_sections, axis=x.order.axes[c_op.axis])(x)
    for wref_c_y, w_y in zip(c_op.outputs, ys):
        converter.set_variable(wref_c_y(), w_y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Squeeze")
def _convert_squeeze(converter: ChainerConverter, c_op: "chainer.functions.Squeeze"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Squeeze is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Swapaxes")
def _convert_swapaxes(converter: ChainerConverter, c_op: "chainer.functions.Swapaxes"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Swapaxes is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Tile")
def _convert_tile(converter: ChainerConverter, c_op: "chainer.functions.Tile"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Tile is not supported")


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Transpose")
def _convert_transpose(converter: ChainerConverter, c_op: "chainer.functions.Transpose"):
    # TODO
    raise NotImplementedError("[ChainerConverter] Transpose is not supported")


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
