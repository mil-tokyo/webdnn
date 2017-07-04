from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.relu import Relu

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
relu: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
    var val = x[i];
    y[i] = val >= 0.0 ? val : 0.0;
}

},

"""


def relu(op: Relu, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x0"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"relu": source},
        "relu",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size}
    )

    return [kernel]
