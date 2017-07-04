from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.elu import Elu

# EcmaScript3 to support older browsers

source = """
elu: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
    var val = x[i];
    y[i] = val < 0.0 ? (Math.exp(val) - 1.0) : val;
}

},

"""


# noinspection PyUnresolvedReferences
def elu(op: Elu, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x0"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"elu": source},
        "elu",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size}
    )

    return [kernel]
