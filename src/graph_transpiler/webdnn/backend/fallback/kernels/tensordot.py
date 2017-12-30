from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.util.misc import mul

source = """
tensordot: function(input_arrays, output_arrays, option) {
var A = input_arrays[0];
var B = input_arrays[1];
var C = output_arrays[0];

var index2pos = function(index, stride, shape) {
    var i = 0, pos = [];
    for (i = 0; i < stride.length; i++) pos[i] = Math.floor(index / stride[i]) % shape[i];
    return pos;
};

var pos2index = function(pos, stride) {
    var i = 0, index = 0;
    for (i = 0; i < stride.length; i++) index += pos[i] * stride[i];
    return index;
};

var c_index, c_pos;
var a_base_index, a_offset;
var b_base_index, b_offset;
var i;
var sum = 0;
for (c_index = 0; c_index < C.length; c_index++) {
    c_pos = index2pos(c_index, option.stride_C, option.shape_C);
    a_base_index = pos2index(c_pos, option.stride_A_for_C_axes);
    b_base_index = pos2index(c_pos, option.stride_B_for_C_axes);

    sum = 0;
    for (i = 0; i < option.reduction_size; i++) {
        a_offset = pos2index(index2pos(i, option.stride_A_reduced_axes, option.shape_A_reduced_axes), option.stride_A_reduced_axes_whole);
        b_offset = pos2index(index2pos(i, option.stride_B_reduced_axes, option.shape_B_reduced_axes), option.stride_B_reduced_axes_whole);

        sum += A[a_base_index + a_offset] * B[b_base_index + b_offset];
    }
    C[c_index] = sum;
}

},


"""


@FallbackDescriptorGenerator.register_handler(Tensordot)
def tensordot(op: Tensordot, memory_layout: MemoryLayout) -> List[Kernel]:
    A = op.inputs["A"]
    B = op.inputs["B"]
    C = op.outputs["C"]

    shape_A_reduced_axes = [A.shape_dict[a] for a in op.axes[0]]
    shape_B_reduced_axes = [B.shape_dict[a] for a in op.axes[1]]
    kernel = Kernel(
        {"tensordot": source},
        "tensordot",
        inputs=[memory_layout[A], memory_layout[B]],
        outputs=[memory_layout[C]],
        call_option={"reduction_size": mul(A.shape_dict[a] for a in op.axes[0]),
                     "stride_A": A.stride,
                     "stride_B": B.stride,
                     "stride_C": C.stride,
                     "shape_C": C.shape,
                     "stride_A_for_C_axes": [0 if a not in A.order.axes or a in op.axes[0] else A.stride_dict[a] for a in C.order.axes],
                     "stride_B_for_C_axes": [0 if a not in B.order.axes or a in op.axes[1] else B.stride_dict[a] for a in C.order.axes],
                     "shape_A_reduced_axes": shape_A_reduced_axes,
                     "stride_A_reduced_axes": [mul(shape_A_reduced_axes[i + 1:]) for i in range(len(shape_A_reduced_axes))],
                     "stride_A_reduced_axes_whole": [A.stride_dict[a] for a in op.axes[0]],
                     "shape_B_reduced_axes": shape_B_reduced_axes,
                     "stride_B_reduced_axes": [mul(shape_B_reduced_axes[i + 1:]) for i in range(len(shape_B_reduced_axes))],
                     "stride_B_reduced_axes_whole": [B.stride_dict[a] for a in op.axes[1]]}
    )

    return [kernel]
