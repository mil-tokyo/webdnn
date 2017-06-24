from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.sigmoid import Sigmoid

# EcmaScript3 to support older browsers

source = """
sigmoid: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
    var val = x[i];
    y[i] = 1.0 / (1.0 + Math.exp(-val));
}

},

"""


# noinspection PyUnresolvedReferences
def sigmoid(op: Sigmoid, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"sigmoid": source},
        "sigmoid",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size}
    )

    return [kernel]
