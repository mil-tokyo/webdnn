from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.concat import Concat

source = """
concat: function(input_arrays, output_arrays, option) {
var xs = input_arrays;
var y = output_arrays[0];
var shapes = option.x_shapes;
var strides = option.x_strides;
var offsets = option.x_offsets;
var x;
var offset;
var stride;
var shape;
var position;

for (var i = 0; i < xs.length; i++) {
    x = xs[i];
    offset = offsets[i];
    stride = strides[i];
    shape = shapes[i];
    position = [];

    for (var j = 0; j < shape.length; j++) {
        position[j] = 0;
    }

    do {
        y[offset + dot(stride, position)] = get(x, shape, position);
    } while (increment(shape, position))
}

function dot(a, b) {
    var sum = 0;
    for (var i = 0; i < a.length; i++) {
        sum += a[i] * b[i];
    }
    return sum;
}

function get(x, shape, position) {
    var i = 0;
    for (var j = 0; j < shape.length; j++) {
        i = (i * shape[j]) + position[j];
    }
    return x[i];
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
@FallbackDescriptorGenerator.register_handler(Concat)
def concat(op: Concat, memory_layout: MemoryLayout) -> List[Kernel]:
    xs = [op.inputs[f"x{i}"] for i in range(len(op.inputs))]
    y = op.outputs["y"]
    target_axis = op.axis
    x_shapes = [x.shape for x in xs]

    y_strides = []
    stride = 1
    for s in reversed(y.shape):
        y_strides.insert(0, stride)
        stride *= s

    # x_strides[i][j] is stride size of xs[i].order.axes[j] in y
    x_strides = [[] for _ in xs]
    for x, strides in zip(xs, x_strides):
        for axis in x.order.axes:
            strides.append(y_strides[y.order.axes_dict[axis]])

    # x_offsets[i] is memory offset of xs[i]'s data in y.
    x_offsets = []
    target_axis_offset = 0
    for x in xs:
        x_offsets.append(target_axis_offset * y_strides[y.order.axes_dict[target_axis]])
        target_axis_offset += x.shape_dict[target_axis]

    # (destination address of xs[i][d_0, ..., d_n]) = x_offsets[i] + x_strides[i][0] * d_0 + ... + x_strides[i][n] * d_n
    kernel = Kernel(
        {"concat": source},
        "concat",
        inputs=[memory_layout[x] for x in xs],
        outputs=[memory_layout[y]],
        call_option={"x_shapes": x_shapes,
                     "x_strides": x_strides,
                     "x_offsets": x_offsets}
    )

    return [kernel]
