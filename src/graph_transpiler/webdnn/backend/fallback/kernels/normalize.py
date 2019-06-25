from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.normalize import Normalize

# EcmaScript3 to support older browsers

source = """
normalize: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var N = option.N | 0;
var C = option.C | 0;
var eps = +option.eps;

for (var n = 0; n < N; n++) {
    var sq_sum = 0.0;
    for (var c = 0; c < C; c++) {
        var val = x[n * C + c];
        sq_sum += val * val;
    }

    sq_sum = 1.0 / (Math.sqrt(sq_sum) + eps);
    for (var c = 0; c < C; c++) {
        var val = x[n * C + c];
        y[n * C + c] = val * sq_sum;
    }
}
},

"""


# noinspection PyUnusedLocal
@FallbackDescriptorGenerator.register_handler(Normalize)
def normalize(op: Normalize, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert y.order == x.order
    assert y.shape == x.shape

    axis = op.parameters["axis"]
    assert axis == x.order.axes[-1], "[Fallback] Normalize supports only for aggregating last axis."

    kernel = Kernel(
        {"normalize": source},
        "normalize",
        inputs=[memory_layout[x]],
        outputs=[memory_layout[y]],
        call_option={
            "N": y.size // y.shape_dict[axis],
            "C": y.shape_dict[axis],
            "eps": op.parameters["eps"]}
    )

    return [kernel]
