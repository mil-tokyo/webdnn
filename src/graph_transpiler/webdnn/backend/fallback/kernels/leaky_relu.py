from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.leaky_relu import LeakyRelu

# EcmaScript3 to support older browsers

source = """
leaky_relu: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;
var slope = option.slope;

for (var i = 0; i < length; i++) {
    var val = x[i];
    y[i] = val >= 0.0 ? val : val * slope;
}

},

"""


# noinspection PyUnresolvedReferences
def leaky_relu(op: LeakyRelu, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x0"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"leaky_relu": source},
        "leaky_relu",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size, "slope": op.parameters["slope"]}
    )

    return [kernel]
