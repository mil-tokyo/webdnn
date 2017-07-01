from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.order import OrderNCHW, OrderNC, OrderNHWC

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
flatten: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
  y[i] = x[i];
}

},

"""


# noinspection PyUnusedLocal
def flatten(op: Flatten, memory_layout: MemoryLayout) -> List[Kernel]:
    # データ変換がない場合のみ現状サポート
    # 該当軸のsize, strideを与える
    x = op.inputs["x"]
    y = op.outputs["y"]

    if x.order == OrderNCHW:
        assert y.order == OrderNC
    elif x.order == OrderNHWC:
        assert y.order == OrderNC
    else:
        raise AssertionError("Unsupported order")

    kernel = Kernel(
        {"flatten": source},
        "flatten",
        inputs=[x],
        outputs=[y],
        call_option={"length": x.size}
    )

    return [kernel]
