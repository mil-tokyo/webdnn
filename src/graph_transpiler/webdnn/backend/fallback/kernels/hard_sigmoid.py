from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.hard_sigmoid import HardSigmoid

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
hard_sigmoid: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
    var val = x[i];
    val = val * 0.2 + 0.5;
    if (val < 0.0) {
        val = 0.0;
    } else if (val > 1.0) {
        val = 1.0;
    }
    y[i] = val;
}

},

"""


# noinspection PyUnresolvedReferences
def hard_sigmoid(op: HardSigmoid, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"hard_sigmoid": source},
        "hard_sigmoid",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size}
    )

    return [kernel]
