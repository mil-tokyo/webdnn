from typing import List

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.backend.fallback.operators.operator import Operator

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers
linear_mul_source = """
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


class Linear(Operator):
    name: str = "linear"

    def convert_to_kernels(self,
                           batch_size: int) -> List[Kernel]:
        source = linear_mul_source

        kernel = Kernel(
            {self.name: source},
            self.name,
            inputs=[v.name for v in self.inputs],
            outputs=[v.name for v in self.outputs],
            params=[self.layer.name + "/W"],
            call_option={"m": batch_size,
                         "n": self.layer.parameters["out_size"],
                         "k": self.layer.parameters["in_size"]}
        )

        return [kernel]
