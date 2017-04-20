from typing import List

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.graph import Operator

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
axiswise_bias: function(input_arrays, output_arrays, param_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var b = param_arrays[0];
var n = option.n | 0;
var c = option.c | 0;

for (var i = 0; i < n; i++) {
  for (var j = 0; j < c; j++) {
    y[i * c + j] = x[i * c + j] + b[j];
  }
}

},

"""


def axiswise_bias(op: Operator) -> List[Kernel]:
    x = op.inputs["x"]
    b = op.inputs["b"]
    y = op.outputs["y"]

    assert x.ndim == 2
    assert y.ndim == 2
    assert x.axis_order.axes_dict[op.parameters["axis"]] == 1

    kernel = Kernel(
        {"axiswise_bias": source},
        "axiswise_bias",
        inputs=[x.parameters["name"]],
        outputs=[y.parameters["name"]],
        weights=[b.parameters["name"]],
        call_option={"n": x.shape[0],
                     "c": x.shape[1]}
    )

    return [kernel]
