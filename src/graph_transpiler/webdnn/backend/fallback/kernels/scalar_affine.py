from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers
from webdnn.graph.operators.scalar_affine import ScalarAffine

source = """
scalar_affine: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;
var s = option.s | 0;
var b = option.b | 0;

for (var i = 0; i < length; i++) {
    var val = x[i];
    y[i] = x[i] * s + b;
}

},

"""


def scalar_affine(op: ScalarAffine, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"scalar_affine": source},
        "scalar_affine",
        inputs=[x],
        outputs=[y],
        call_option={
            "length": x.size,
            "s": op.scale,
            "b": op.bias
    }
    )

    return [kernel]
