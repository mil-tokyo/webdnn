from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.elementwise_mul import ElementwiseMul

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
elementwise_mul: function(input_arrays, output_arrays, option) {
var x0 = input_arrays[0];
var x1 = input_arrays[1];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
    y[i] = x0[i] * x1[i];
}

},

"""


# noinspection PyUnusedLocal
def elementwise_mul(op: ElementwiseMul, memory_layout: MemoryLayout) -> List[Kernel]:
    assert len(op.inputs) == 2
    x0 = op.inputs["x0"]
    x1 = op.inputs["x1"]
    y = op.outputs["y"]
    assert x0.shape == x1.shape == y.shape
    assert x0.order == x1.order == y.order

    kernel = Kernel(
        {"elementwise_mul": source},
        "elementwise_mul",
        inputs=[x0, x1],
        outputs=[y],
        call_option={"length": x0.size}
    )

    return [kernel]
