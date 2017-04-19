from typing import List

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.graph import Operator

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
relu: function(input_arrays, output_arrays, param_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
    var val = x[i];
    y[i] = val >= 0.0 ? val : 0.0;
}

},

"""


def relu(op: Operator) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"relu": source},
        "relu",
        inputs=[x.parameters["name"]],
        outputs=[y.parameters["name"]],
        weights=[],
        call_option={"length": x.size}
    )

    return [kernel]
