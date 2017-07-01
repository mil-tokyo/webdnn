from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.softplus import Softplus

# EcmaScript3 to support older browsers

source = """
softplus: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;
var beta = option.beta;
var beta_inv = 1.0 / beta;

for (var i = 0; i < length; i++) {
    var val = x[i];
    y[i] = Math.log(1.0 + Math.exp(beta * val)) * beta_inv;
}

},

"""


# noinspection PyUnresolvedReferences
def softplus(op: Softplus, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"softplus": source},
        "softplus",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size, "beta": op.parameters["beta"]}
    )

    return [kernel]
