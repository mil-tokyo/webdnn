from typing import List

import numpy as np

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.graph import Operator
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
flatten: function(input_arrays, output_arrays, param_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var length = option.length | 0;

for (var i = 0; i < length; i++) {
  y[i] = x[i];
}

},

"""


def flatten(op: Operator) -> List[Kernel]:
    # データ変換がない場合のみ現状サポート
    # 該当軸のsize, strideを与える
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert set(op.parameters["in_axes"]) == {A.Axis.C, A.Axis.H, A.Axis.W}
    assert set(op.parameters["out_axes"]) == {A.Axis.C}
    if x.axis_order is VA.OrderNCHW:
        assert y.axis_order is VA.OrderNC
    elif x.axis_order is VA.OrderNHWC:
        assert y.axis_order is VA.OrderNC
        # H, W == 1
        assert x.shape[1] == 1
        assert x.shape[2] == 1

    kernel = Kernel(
        {"flatten": source},
        "flatten",
        inputs=[x.parameters["name"]],
        outputs=[y.parameters["name"]],
        weights=[],
        call_option={"length": x.size}
    )

    return [kernel]
