from typing import List

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.backend.fallback.operators.operator import Operator

# assume (batch_size, ..., out_size), C-order
# EcmaScript3 to support older browsers
channelwise_bias_source = """
channelwise_bias: function(input_arrays, output_arrays, param_arrays, option) {
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


class ChannelwiseBias(Operator):
    name: str = "channelwise_bias"

    def convert_to_kernels(self,
                           batch_size: int) -> List[Kernel]:
        source = channelwise_bias_source
        input_shape = self.inputs[0].shape
        assert self.layer.parameters["out_size"] == input_shape[-1]
        n = 1
        for s in input_shape[:-1]:
            n *= s

        kernel = Kernel(
            {self.name: source},
            self.name,
            inputs=[v.name for v in self.inputs],
            outputs=[v.name for v in self.outputs],
            weights=[self.layer.name + "/b"],
            call_option={"n": n,
                         "c": self.layer.parameters["out_size"]}
        )

        return [kernel]
