from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.clipped_relu import ClippedRelu

# EcmaScript3 to support older browsers

source = """
clipped_relu: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;
var cap = option.cap;

for (var i = 0; i < length; i++) {
    var val = x[i];
    y[i] = val >= 0.0 ? (val < cap ? val : cap) : 0.0;
}

},

"""


# noinspection PyUnresolvedReferences
def clipped_relu(op: ClippedRelu, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x0"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"clipped_relu": source},
        "clipped_relu",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size, "cap": op.parameters["cap"]}
    )

    return [kernel]
