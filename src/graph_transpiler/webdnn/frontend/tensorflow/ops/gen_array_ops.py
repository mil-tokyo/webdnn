import itertools
from typing import List

import numpy as np
import tensorflow as tf
from tensorflow.python.framework.tensor_util import MakeNdarray

from webdnn.frontend.tensorflow.converter import TensorFlowConverter
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.operators.slice import Slice
from webdnn.graph.operators.space2depth import Space2Depth
from webdnn.graph.operators.tile import Tile
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.operators.zero_padding_2d import ZeroPadding2D
from webdnn.graph.order import Order, OrderNHWC
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console
from webdnn.util.misc import mul


@TensorFlowConverter.register_handler("BatchMatrixBandPart")
def batch_matrix_band_part_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("BatchMatrixDiag")
def batch_matrix_diag_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("BatchMatrixDiagPart")
def batch_matrix_diag_part_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("BatchMatrixSetDiag")
def batch_matrix_set_diag_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("BatchToSpace")
def batch_to_space_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("BatchToSpaceND")
def batch_to_space_nd_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Bitcast")
def bitcast_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("CheckNumerics")
def check_numerics_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Concat")
def concat_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ConcatOffset")
def concat_offset_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ConcatV2")
def concat_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    xs = [converter.get_variable(tf_tensor) for tf_tensor in tf_op.inputs]
    axis = xs.pop()
    # TODO
    assert isinstance(axis, ConstantVariable), "[TensorFlowConverter] Dynamic axis concatenation is not supported yet."
    axis = xs[0].order.axes[int(axis.data.flatten()[0])]

    for x0, x1 in itertools.permutations(xs, r=2):
        x0.order.unify(x1.order)

    y, = Concat(None, axis=axis)(*xs)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Const")
def const_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    tensor = tf_op.outputs[0]
    shape = [Placeholder() if dim.value is None else dim.value for dim in tensor.shape.dims]
    value = MakeNdarray(tf_op.get_attr("value"))

    if len(shape) == 0:
        # Scalar variable
        variable = ConstantVariable(value.reshape([1]), Order([None]))

    else:
        variable = ConstantVariable(value, Order([None] * len(shape)))

    converter.set_variable(tensor, variable)


@TensorFlowConverter.register_handler("DepthToSpace")
def depth_to_space_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    x.order.unify(OrderNHWC)

    y, = Depth2Space(None, r=tf_op.get_attr("block_size"))(x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Dequantize")
def dequantize_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Diag")
def diag_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("DiagPart")
def diag_part_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("EditDistance")
def edit_distance_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ExpandDims")
def expand_dims_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    dim = converter.get_variable(tf_op.inputs[1])

    if not isinstance(dim, ConstantVariable):
        raise NotImplementedError("[TensorFlowConverter] Operator 'ExpandDims' with dynamic dimension is not supported.")

    dim = dim.data.astype(np.int32).flatten()[0]
    new_shape = list(x.shape)
    new_shape.insert(dim, 1)
    new_axes = list(x.order.axes)
    new_axes.insert(dim, Axis())
    converter.set_variable(tf_op.outputs[0], x.reshape(order=Order(new_axes), shape=new_shape))


@TensorFlowConverter.register_handler("ExtractImagePatches")
def extract_image_patches_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FakeQuantWithMinMaxArgs")
def fake_quant_with_min_max_args_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FakeQuantWithMinMaxArgsGradient")
def fake_quant_with_min_max_args_gradient_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FakeQuantWithMinMaxVars")
def fake_quant_with_min_max_vars_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FakeQuantWithMinMaxVarsGradient")
def fake_quant_with_min_max_vars_gradient_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FakeQuantWithMinMaxVarsPerChannel")
def fake_quant_with_min_max_vars_per_channel_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FakeQuantWithMinMaxVarsPerChannelGradient")
def fake_quant_with_min_max_vars_per_channel_gradient_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Fill")
def fill_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Gather")
def gather_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("GatherNd")
def gather_nd_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("GatherV2")
def gather_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Identity")
def identity_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    converter.set_variable(tf_op.outputs[0], converter.get_variable(tf_op.inputs[0]))


@TensorFlowConverter.register_handler("ImmutableConst")
def immutable_const_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("InvertPermutation")
def invert_permutation_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ListDiff")
def list_diff_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MatrixBandPart")
def matrix_band_part_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MatrixDiag")
def matrix_diag_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MatrixDiagPart")
def matrix_diag_part_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MatrixSetDiag")
def matrix_set_diag_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MirrorPad")
def mirror_pad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])

    padding = converter.get_variable(tf_op.inputs[1])
    if not isinstance(padding, ConstantVariable):
        raise NotImplementedError('[TensorFlowConverter] PadV2 with dynamic padding size is not supported')

    padding = padding.data.astype(np.int).tolist()

    mode = tf_op.get_attr("mode")  # type: bytes

    for axis, (pad_begin, pad_end) in zip(x.order.axes, padding):
        xs = []

        if pad_begin > 0:
            if mode == b'SYMMETRIC':
                slices = [slice(pad_begin - 1, None, -1) if a == axis else slice(None) for a in x.order.axes]

            elif mode == b'REFLECT':
                slices = [slice(pad_begin, 0, -1) if a == axis else slice(None) for a in x.order.axes]

            else:
                raise NotImplementedError(f"[TensorFlowConverter] Unknown mirror pad mode: {mode}")

            xs.append(x[slices])

        xs.append(x)

        if pad_end > 0:
            if mode == b'SYMMETRIC':
                slices = [slice(-1, - 1 - pad_end, -1) if a == axis else slice(None) for a in x.order.axes]

            elif mode == b'REFLECT':
                slices = [slice(-2, - 2 - pad_end, -1) if a == axis else slice(None) for a in x.order.axes]

            else:
                raise NotImplementedError(f"[TensorFlowConverter] Unknown mirror pad mode: {mode}")

            xs.append(x[slices])

        if len(xs) > 1:
            x, = Concat(None, axis=axis)(*xs)

    converter.set_variable(tf_op.outputs[0], x)


@TensorFlowConverter.register_handler("MirrorPadGrad")
def mirror_pad_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("OneHot")
def one_hot_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("OnesLike")
def ones_like_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Pack")
def pack_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Pad")
def pad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])

    padding = converter.get_variable(tf_op.inputs[1])
    if not isinstance(padding, ConstantVariable):
        raise NotImplementedError('[TensorFlowConverter] Pad with dynamic padding size is not supported')

    padding = padding.data.astype(np.int).tolist()  # type: List[List[int]]

    if x.order.check_same_axes(OrderNHWC) and all([
        padding[x.order.axes_dict[Axis.N]][0] == padding[x.order.axes_dict[Axis.N]][1] == 0,
        padding[x.order.axes_dict[Axis.H]][0] == padding[x.order.axes_dict[Axis.H]][1],
        padding[x.order.axes_dict[Axis.W]][0] == padding[x.order.axes_dict[Axis.W]][1],
        padding[x.order.axes_dict[Axis.C]][0] == padding[x.order.axes_dict[Axis.C]][1] == 0
    ]):
        # Padding for only spatial axes: use ZeroPadding2D
        y, = ZeroPadding2D(None, padding=(padding[x.order.axes_dict[Axis.H]][0], padding[x.order.axes_dict[Axis.W]][0]))(x)

    else:
        # General case: Use Concat
        for axis, (pad_begin, pad_end) in zip(x.order.axes, padding):
            xs = []

            if pad_begin > 0:
                xs.append(ConstantVariable(np.zeros([pad_begin if a is axis else x.shape_dict[a] for a in x.order.axes]), x.order))

            xs.append(x)

            if pad_end > 0:
                xs.append(ConstantVariable(np.zeros([pad_end if a is axis else x.shape_dict[a] for a in x.order.axes]), x.order))

            if len(xs) > 1:
                x, = Concat(None, axis=axis)(*xs)

        y = x

    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("PadV2")
def pad_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])

    padding = converter.get_variable(tf_op.inputs[1])
    if not isinstance(padding, ConstantVariable):
        raise NotImplementedError('[TensorFlowConverter] PadV2 with dynamic padding size is not supported')

    padding = padding.data.astype(np.int).tolist()

    constant_values = converter.get_variable(tf_op.inputs[2]).change_order(x.order)

    for axis, (pad_begin, pad_end) in zip(x.order.axes, padding):
        xs = []

        if pad_begin > 0:
            multiplier = AxisKeyDict(x.order.axes, [pad_begin if a == axis else x.shape_dict[a] for a in x.order.axes])
            xs.append(Tile(None, multiplier)(constant_values)[0])

        xs.append(x)

        if pad_end > 0:
            multiplier = AxisKeyDict(x.order.axes, [pad_end if a == axis else x.shape_dict[a] for a in x.order.axes])
            xs.append(Tile(None, multiplier)(constant_values)[0])

        if len(xs) > 1:
            x, = Concat(None, axis=axis)(*xs)

    converter.set_variable(tf_op.outputs[0], x)


@TensorFlowConverter.register_handler("ParallelConcat")
def parallel_concat_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Placeholder")
def placeholder_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    shape = [Placeholder() if dim.size() is -1 else dim.size() for dim in tf_op.get_attr("shape").dim]
    if any(not Placeholder.check_resolved(s) for s in shape):
        raise NotImplementedError(f"[TensorFlowConverter] Operator \"Placeholder\" with dynamic shape variable is not supported yet.")

    converter.set_variable(tf_op.outputs[0], Variable(shape, Order([None for _ in shape])))


@TensorFlowConverter.register_handler("PlaceholderV2")
def placeholder_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("PlaceholderWithDefault")
def placeholder_with_default_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("PreventGradient")
def prevent_gradient_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizeAndDequantize")
def quantize_and_dequantize_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizeAndDequantizeV2")
def quantize_and_dequantize_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizeAndDequantizeV3")
def quantize_and_dequantize_v3_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizeV2")
def quantize_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedConcat")
def quantized_concat_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedInstanceNorm")
def quantized_instance_norm_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedReshape")
def quantized_reshape_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Rank")
def rank_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = ConstantVariable(np.array([x.ndim]), Order([None]))

    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("RefIdentity")
def ref_identity_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Reshape")
def reshape_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    shape = converter.get_variable(tf_op.inputs[1])

    assert isinstance(shape, ConstantVariable), NotImplementedError(
        f"[TensorFlowConverter] 'Shape' operator with dynamic shape is not supported.")

    shape = shape.data.astype(np.int).flatten().tolist()  # type: List[int]
    if -1 in shape:
        i = shape.index(-1)
        shape.remove(-1)
        shape.insert(i, x.size // (mul(shape)))

    y = x.reshape(shape, Order([None] * len(shape)))
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("ResourceStridedSliceAssign")
def resource_strided_slice_assign_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Reverse")
def reverse_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReverseSequence")
def reverse_sequence_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReverseV2")
def reverse_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ScatterNd")
def scatter_nd_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ScatterNdNonAliasingAdd")
def scatter_nd_non_aliasing_add_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Shape")
def shape_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    assert all(Placeholder.check_resolved(s) for s in x.shape), "[TensorFlowConverter] op 'Shape' with dynamic shape is not supported yet. "

    y = ConstantVariable(np.array(x.shape), Order([None]))
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("ShapeN")
def shape_n_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Size")
def size_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Slice")
def slice_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    begin = converter.get_variable(tf_op.inputs[1])
    size = converter.get_variable(tf_op.inputs[2])

    assert isinstance(begin, ConstantVariable), "[TensorFlowConverter] op 'Slice' with dynamic position is not supported yet. "
    assert isinstance(size, ConstantVariable), "[TensorFlowConverter] op 'Slice' with dynamic size is not supported yet. "

    begin = begin.data.flatten().astype(np.int32).tolist()
    size = size.data.flatten().astype(np.int32).tolist()
    y, = Slice(None, indices=AxisKeyDict(x.order.axes, [slice(b, b + s) for b, s in zip(begin, size)]))(x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("SpaceToBatch")
def space_to_batch_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SpaceToBatchND")
def space_to_batch_nd_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SpaceToDepth")
def space_to_depth_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    x.order.unify(OrderNHWC)

    y, = Space2Depth(None, r=tf_op.get_attr("block_size"))(x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Split")
def split_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SplitV")
def split_v_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Squeeze")
def squeeze_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    squeeze_dims = tf_op.get_attr("squeeze_dims")  # type: List[int]

    in_var = converter.get_variable(tf_op.inputs[0])
    in_var_shape = in_var.shape
    out_var_shape = []  # type: List[int]
    out_var_order = []  # type: List[Axis]
    for dim in range(len(in_var_shape)):
        if dim in squeeze_dims:
            assert in_var_shape[dim] == 1, f"[TensorFlowConverter] {tf_op.type}: dimension to be squeezed have to be 1."
        else:
            out_var_shape.append(in_var_shape[dim])
            out_var_order.append(in_var.order.axes[dim])

    out_var = in_var.reshape(out_var_shape, Order(out_var_order))
    out_tf_var = tf_op.outputs[0]
    converter.set_variable(out_tf_var, out_var)


@TensorFlowConverter.register_handler("StopGradient")
def stop_gradient_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    console.warning("[TensorFlowConverter] StopGradient is ignored.")
    converter.set_variable(tf_op.outputs[0], converter.get_variable(tf_op.inputs[0]))


@TensorFlowConverter.register_handler("StridedSlice")
def strided_slice_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])

    begin = converter.get_variable(tf_op.inputs[1])
    end = converter.get_variable(tf_op.inputs[2])
    strides = converter.get_variable(tf_op.inputs[3])

    assert isinstance(begin, ConstantVariable), "[TensorFlowConverter] op 'Slice' with dynamic index is not supported yet. "
    assert isinstance(end, ConstantVariable), "[TensorFlowConverter] op 'Slice' with dynamic index is not supported yet. "
    assert isinstance(strides, ConstantVariable), "[TensorFlowConverter] op 'Slice' with dynamic index is not supported yet. "

    begin_mask = tf_op.get_attr("begin_mask")
    end_mask = tf_op.get_attr("end_mask")
    ellipsis_mask = tf_op.get_attr("ellipsis_mask")
    new_axis_mask = tf_op.get_attr("new_axis_mask")
    shrink_axis_mask = tf_op.get_attr("shrink_axis_mask")

    begin = begin.data.flatten().astype(np.int32).tolist()  # type: List[int]
    end = end.data.flatten().astype(np.int32).tolist()  # type: List[int]
    strides = strides.data.flatten().astype(np.int32).tolist()  # type: List[int]

    for i in range(x.ndim):
        if begin_mask & (1 << i):
            begin[i] = None

        if end_mask & (1 << i):
            end[i] = None

    slices = []
    for i in range(len(begin)):
        if ellipsis_mask & (1 << i):
            slices.append(Ellipsis)

        elif new_axis_mask & (1 << i):
            # insert new axis
            slices.append(None)

        elif shrink_axis_mask & (1 << i):
            # shrink axis
            slices.append(begin[i])

        else:
            # general slice
            slices.append(slice(begin[i], end[i], strides[i]))

    y = x[slices]
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("StridedSliceAssign")
def strided_slice_assign_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("StridedSliceGrad")
def strided_slice_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Tile")
def tile_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    multiplier = converter.get_variable(tf_op.inputs[1])

    if not isinstance(multiplier, ConstantVariable):
        raise NotImplementedError("[TensorFlowConverter] Operator 'Tile' with dynamic multiplier is not supported yet.")

    multiplier = AxisKeyDict(x.order.axes, multiplier.data.astype(int).flatten().tolist())
    y, = Tile(None, multiplier=multiplier)(x)

    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("TileGrad")
def tile_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Transpose")
def transpose_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    indices = converter.get_variable(tf_op.inputs[1])

    if not isinstance(indices, ConstantVariable):
        raise NotImplementedError("[TensorFlowConverter] Operator 'Transpose' with dynamic indices is not supported yet.")

    indices = indices.data.astype(int).flatten().tolist()  # type: List[int]
    y, = Transpose(None)(x)
    y.change_order(Order([x.order.axes[i] for i in indices]))

    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Unique")
def unique_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("UniqueWithCounts")
def unique_with_counts_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Unpack")
def unpack_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Where")
def where_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ZerosLike")
def zeros_like_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")
