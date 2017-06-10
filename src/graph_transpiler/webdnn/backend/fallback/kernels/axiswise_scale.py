from typing import List

import numpy as np

from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.axiswise_scale import AxiswiseScale

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers
from webdnn.graph.place_holder import PlaceHolder

source = """
axiswise_scale: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var s = input_arrays[1];
var y = output_arrays[0];
var n = option.n | 0;
var axis_stride = option.axis_stride | 0;
var axis_size = option.axis_size | 0;

for (var i = 0; i < n; i++) {
    var ch = (i / axis_stride | 0) % axis_size;
    y[i] = x[i] * s[ch];
}

},

"""


def axiswise_scale(op: AxiswiseScale) -> List[Kernel]:
    # 該当軸のsize, strideを与える
    x = op.inputs["x"]
    s = op.inputs["s"]
    y = op.outputs["y"]

    assert s.ndim == 1
    axis_pos = x.order.axes_dict[op.parameters["axis"]]  # NCHWでaxis=Cなら、1
    axis_size = x.shape[axis_pos]
    assert axis_size == s.size

    axis_stride = np.product(x.shape[axis_pos + 1:])  # NCHWでaxis=Cなら、size(H)*size(W), np.product([])==1.0

    kernel = Kernel(
        {"axiswise_scale": source},
        "axiswise_scale",
        inputs=[x, s],
        outputs=[y],
        call_option={"n": x.size,
                     "axis_stride": axis_stride,
                     "axis_size": axis_size}
    )

    return [kernel]
