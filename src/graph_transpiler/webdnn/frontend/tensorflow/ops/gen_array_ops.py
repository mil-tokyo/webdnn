from typing import List

import numpy as np
import tensorflow as tf

from webdnn import ConstantVariable
from webdnn.frontend.constraints import AxisVar, unify_order
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.zero_padding_2d import ZeroPadding2D
from webdnn.graph.variable import Variable
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.order import Order, OrderNC, OrderNTC, OrderNHWC, OrderC
from webdnn.graph.placeholder import Placeholder
from webdnn.frontend.tensorflow.converter import TensorFlowConverter


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
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Const")
def const_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # FIXME: should output ConstantVariable?
    tensor = tf_op.outputs[0]
    shape = [Placeholder() if dim.value is None else dim.value for dim in tensor.shape.dims]
    if len(shape) == 0:
        # Scalar variable
        # WebDNN's variable should have at least 1 dimension
        variable = ConstantVariable(np.array([tf_op.get_attr("value").float_val._values[0]], dtype=np.float32),
                                    Order([Axis.C]))
    else:
        variable = Variable(shape, Order([AxisVar() for _ in shape]))
    converter.set_variable(tensor, variable)


@TensorFlowConverter.register_handler("DepthToSpace")
def depth_to_space_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


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
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


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
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


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
    # Zero padding
    # FIXME: currently, determining padding from shape of input / output. Originally, determining by inputs[1] is correct.

    in_var = converter.get_variable(tf_op.inputs[0])
    unify_order(in_var.order, OrderNHWC)  # FIXME: assuming input order as NHWC
    out_tf_var = tf_op.outputs[0]
    # calculate output shape from out_tf_var.shape and in_var.shape
    # ZeroPadding2D operator only accepts padding for H and W axes.
    padding = [0, 0]
    for dim in range(in_var.ndim):
        in_size = in_var.shape[dim]
        out_size = out_tf_var.shape.dims[dim].value
        assert isinstance(in_size, int), "[TensorFlowConverter] Pad: Placeholder for input shape is not supported yet."
        assert isinstance(out_size, int), "[TensorFlowConverter] Pad: Placeholder for output shape is not supported yet."
        axis = in_var.order.axes[dim]
        if axis in [Axis.H, Axis.W]:
            assert (out_size - in_size % 2) != 0, "[TensorFlowConverter] Pad: Uneven padding is not supported yet."
            pad_size = (out_size - in_size) // 2
            if axis == Axis.H:
                padding[0] = pad_size
            elif axis == Axis.W:
                padding[1] = pad_size
        else:
            assert out_size == in_size, "[TensorFlowConverter] Pad: padding for axis other than H and W is not supported yet."
    out_var, = ZeroPadding2D(None, padding=tuple(padding))(in_var)
    converter.set_variable(out_tf_var, out_var)


@TensorFlowConverter.register_handler("PadV2")
def pad_v2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ParallelConcat")
def parallel_concat_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Placeholder")
def placeholder_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


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
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("RefIdentity")
def ref_identity_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Reshape")
def reshape_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    # input: data, output_shape
    # output: reshaped_data
    # Currently, ignores output_shape.
    in_var = converter.get_variable(tf_op.inputs[0])
    out_tf_var = tf_op.outputs[0]
    # calculate output shape from out_tf_var.shape and in_var.shape
    # out_tf_var.shape can have at most one placeholder.
    out_placeholder_count = 0
    out_placeholder_idx = None
    out_constant_prod = 1
    out_shape = []
    for i, dim_size in enumerate(out_tf_var.shape.dims):
        out_shape.append(dim_size.value)
        if dim_size.value is None:
            out_placeholder_count += 1
            out_placeholder_idx = i
        else:
            out_constant_prod *= dim_size.value
    if out_placeholder_count > 1:
        raise NotImplementedError(
            "[TensorFlowConverter] Reshape: output with more than one placeholder is not supported yet.")
    elif out_placeholder_count == 1:
        if in_var.size % out_constant_prod != 0:
            raise ValueError("[TensorFlowConverter] Reshape: invalid reshape output value.")
        out_shape[out_placeholder_idx] = in_var.size // out_constant_prod
    out_var, = Reshape(None, in_order=in_var.order, out_order=Order([AxisVar() for _ in out_shape]),
                       out_shape=out_shape)(in_var)
    converter.set_variable(out_tf_var, out_var)


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
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ShapeN")
def shape_n_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Size")
def size_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Slice")
def slice_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SpaceToBatch")
def space_to_batch_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SpaceToBatchND")
def space_to_batch_nd_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SpaceToDepth")
def space_to_depth_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


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

    out_var, = Reshape(None, in_order=in_var.order, out_order=Order(out_var_order), out_shape=out_var_shape)(in_var)
    out_tf_var = tf_op.outputs[0]
    converter.set_variable(out_tf_var, out_var)


@TensorFlowConverter.register_handler("StopGradient")
def stop_gradient_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("StridedSlice")
def strided_slice_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("StridedSliceAssign")
def strided_slice_assign_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("StridedSliceGrad")
def strided_slice_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Tile")
def tile_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("TileGrad")
def tile_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Transpose")
def transpose_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


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
