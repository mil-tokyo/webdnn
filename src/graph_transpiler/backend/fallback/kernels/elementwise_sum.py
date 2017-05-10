from typing import List

from graph_transpiler.backend.fallback.kernel import Kernel
from graph_transpiler.graph.operators.elementwise_sum import ElementwiseSum

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
elementwise_sum: function(input_arrays, output_arrays, param_arrays, option) {
var x0 = input_arrays[0];
var x1 = input_arrays[1];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
    y[i] = x0[i] + x1[i];
}

},

"""


def elementwise_sum(op: ElementwiseSum) -> List[Kernel]:
    assert len(op.inputs) == 2
    x0 = op.inputs["x0"]
    x1 = op.inputs["x1"]
    y = op.outputs["y"]
    assert x0.shape == x1.shape
    assert x0.shape == y.shape

    kernel = Kernel(
        {"elementwise_sum": source},
        "elementwise_sum",
        inputs=[x0.parameters["name"], x1.parameters["name"]],
        outputs=[y.parameters["name"]],
        weights=[],
        call_option={"length": x0.size}
    )

    return [kernel]
