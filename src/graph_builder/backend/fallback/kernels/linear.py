from typing import List

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.graph import Operator
from graph_builder.graph.operators import attributes as A

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
linear: function(input_arrays, output_arrays, param_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var w = param_arrays[0];
var m = option.m | 0;
var n = option.n | 0;
var k = option.k | 0;

for (var i = 0; i < m; i++) {
  for (var j = 0; j < n; j++) {
    var sum = 0.0;
    for (var s = 0; s < k; s++) {
      sum += x[i * k + s] * w[s * n + j];
    }
    y[i * n + j] = sum;
  }
}

},


"""


def linear(op: Operator) -> List[Kernel]:
    x = op.inputs["x"]
    w = op.inputs["w"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"linear": source},
        "linear",
        inputs=[x.parameters["name"]],
        outputs=[y.parameters["name"]],
        weights=[w.parameters["name"]],
        call_option={"m": x.shape_dict[A.Axis.N],
                     "n": y.shape_dict[A.Axis.C],
                     "k": x.shape_dict[A.Axis.C]}
    )

    return [kernel]
