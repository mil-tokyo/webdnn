from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.tanh import Tanh

# EcmaScript3 to support older browsers
# Math.tanh is EC6 feature

source = """
tanh: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
    var val = x[i];
    var exp2x = Math.exp(2 * val);
    y[i] = (exp2x - 1.0) / (exp2x + 1.0);
}

},

"""


# noinspection PyUnresolvedReferences
def tanh(op: Tanh, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"tanh": source},
        "tanh",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size}
    )

    return [kernel]
