from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.softmax import Softmax

# EcmaScript3 to support older browsers

source = """
softmax: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var N = option.N | 0;
var C = option.C | 0;

for (var n = 0; n < N; n++) {
    var set_max = x[n * C];
    for (var c = 0; c < C; c++) {
        var val = x[n * C + c];
        if (val > set_max) {
            set_max = val;
        }
    }

    var sum_exp = 0.0;
    for (var c = 0; c < C; c++) {
        var val = x[n * C + c];
        var exp_x = Math.exp(val - set_max);
        sum_exp += exp_x;
        y[n * C + c] = exp_x;
    }

    for (var c = 0; c < C; c++) {
        y[n * C + c] /= sum_exp;
    }
}
},

"""


# noinspection PyUnusedLocal
@FallbackDescriptorGenerator.register_handler(Softmax)
def softmax(op: Softmax, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert y.order == x.order
    assert y.shape == x.shape

    axis = op.parameters["axis"]
    assert axis == x.order.axes[-1], "[Fallback] Softmax supports only for aggregating last axis."

    kernel = Kernel(
        {"softmax": source},
        "softmax",
        inputs=[memory_layout[x]],
        outputs=[memory_layout[y]],
        call_option={
            "N": y.size // y.shape_dict[axis],
            "C": y.shape_dict[axis]}
    )

    return [kernel]
