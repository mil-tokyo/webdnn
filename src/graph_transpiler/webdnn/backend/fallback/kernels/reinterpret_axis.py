from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis

# EcmaScript3 to support older browsers

source = """
reinterpret_axis: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
  y[i] = x[i];
}

},

"""


# noinspection PyUnusedLocal
@FallbackDescriptorGenerator.register_handler(ReinterpretAxis)
def reinterpret_axis(op: ReinterpretAxis, memory_layout: MemoryLayout) -> List[Kernel]:
    # Operation without need for transposition is currently supported
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert x.order == op.parameters["in_order"]
    assert y.order == op.parameters["out_order"]

    kernel = Kernel(
        {"reinterpret_axis": source},
        "reinterpret_axis",
        inputs=[memory_layout[x]],
        outputs=[memory_layout[y]],
        call_option={"length": x.size}
    )

    return [kernel]
