from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.split_axis import SplitAxis

source = """
concat: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var ys = output_arrays;
var shapes = option.y_shapes;
var strides = option.y_strides;
var offsets = option.y_offsets;
var y;
var offset;
var stride;
var shape;
var position;

for (var i = 0; i < ys.length; i++) {
    y = ys[i];
    offset = offsets[i];
    stride = strides[i];
    shape = shapes[i];
    position = [];

    for (var j = 0; j < shape.length; j++) {
        position[j] = 0;
    }

    do {
        set(y, shape, position, x[offset + dot(stride, position)]);
    } while (increment(shape, position))
}

function dot(a, b) {
    var sum = 0;
    for (var i = 0; i < a.length; i++) {
        sum += a[i] * b[i];
    }
    return sum;
}

function set(x, shape, position, v) {
    var i = 0;
    for (var j = 0; j < shape.length; j++) {
        i = (i * shape[j]) + position[j];
    }
    x[i] = v;
}

function increment(shape, position) {
    var d = shape.length - 1;
    position[d]++;

    while (position[d] === shape[d]) {
        if (d == 0) return false;

        position[d] -= shape[d];
        d--;
        position[d]++;
    }

    return true;
}

},
"""


# noinspection PyUnusedLocal
@FallbackDescriptorGenerator.register_handler(SplitAxis)
def split_axis(op: SplitAxis, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    ys = [op.outputs[f"y{i}"] for i in range(len(op.outputs))]
    target_axis = op.parameters["axis"]
    y_shapes = [y.shape for y in ys]

    # y_strides[i][j] is stride size of ys[i].order.axes[j] in x
    y_strides = [[] for _ in ys]
    for y, strides in zip(ys, y_strides):
        for axis in y.order.axes:
            strides.append(x.stride[x.order.axes_dict[axis]])

    # y_offsets[i] is memory offset of ys[i]'s data in x.
    y_offsets = []
    target_axis_offset = 0
    for y in ys:
        y_offsets.append(target_axis_offset * x.stride[x.order.axes_dict[target_axis]])
        target_axis_offset += y.shape_dict[target_axis]

    # (destination address of ys[i][d_0, ..., d_n]) = y_offsets[i] + y_strides[i][0] * d_0 + ... + y_strides[i][n] * d_n
    kernel = Kernel(
        {"concat": source},
        "concat",
        inputs=[memory_layout[x]],
        outputs=[memory_layout[y] for y in ys],
        call_option={"y_shapes": y_shapes,
                     "y_strides": y_strides,
                     "y_offsets": y_offsets}
    )

    return [kernel]
