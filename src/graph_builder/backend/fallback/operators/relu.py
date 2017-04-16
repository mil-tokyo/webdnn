from typing import List

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.backend.fallback.operators.operator import Operator

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers
relu_source = """
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


class Relu(Operator):
    name: str = "relu"

    def convert_to_kernels(self,
                           batch_size: int) -> List[Kernel]:
        source = relu_source

        kernel = Kernel(
            {self.name: source},
            self.name,
            inputs=[v.name for v in self.inputs],
            outputs=[v.name for v in self.outputs],
            params=[],
            call_option={"length": batch_size * self.layer.parameters["out_size"]}
        )

        return [kernel]
