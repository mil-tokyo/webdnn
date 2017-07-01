from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.softsign import Softsign

# EcmaScript3 to support older browsers

source = """
softsign: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
    var val = x[i];
    y[i] = val / (Math.abs(val) + 1.0);
}

},

"""


# noinspection PyUnresolvedReferences
def softsign(op: Softsign, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"softsign": source},
        "softsign",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size}
    )

    return [kernel]
