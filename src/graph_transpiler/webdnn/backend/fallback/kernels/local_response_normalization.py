from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.backend.fallback.kernels.util import calculate_stride
from webdnn.graph.axis import Axis
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization

# x: (batch_size, h, w, in_size), w: (kh, kw, in_size, out_size), y: (batch_size, oh, ow, out_size) C-order
# EcmaScript3 to support older browsers

source = """
local_response_normalization: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var n = option.n | 0;
var out_spatial = option.out_spatial;
var out_size = option.out_size | 0;
var p_half_n = option.p_half_n | 0;
var p_k = +option.p_k;
var p_alpha = +option.p_alpha;
var p_minus_beta = +option.p_minus_beta;
var strides_x = option.strides_x;
var strides_y = option.strides_y;

var get_x = function(n_, y_, x_, c_) {
  var idx = n_ * strides_x[0] + y_ * strides_x[1] + x_ * strides_x[2] + c_ * strides_x[3];
  return x[idx];
};

var set_y = function(n_, y_, x_, c_, val) {
  var idx = n_ * strides_y[0] + y_ * strides_y[1] + x_ * strides_y[2] + c_ * strides_y[3];
  y[idx] = val;
};

for (var batch = 0; batch < n; batch++) {
  for (var oy = 0; oy < out_spatial[0]; oy++) {
    for (var ox = 0; ox < out_spatial[1]; ox++) {
      for (var oc = 0; oc < out_size; oc++) {
        var ch_low = oc - p_half_n;
        if (ch_low < 0) {
          ch_low = 0;
        }
        var ch_high = oc + p_half_n + 1;
        if (ch_high > out_size) {
          ch_high = out_size;
        }

        var sq_sum = 0.0;
        for (var ic = ch_low; ic < ch_high; ic++) {
          var val = get_x(batch, oy, ox, ic);
          sq_sum += val * val;
        }

        var scale = Math.pow(sq_sum * p_alpha + p_k, p_minus_beta);
        var ret = get_x(batch, oy, ox, oc) * scale;
        set_y(batch, oy, ox, oc, ret);
      }
    }
  }
}

},

"""


def calculate_all_strides(var):
    return [calculate_stride(var, axis) for axis in [Axis.N, Axis.H, Axis.W, Axis.C]]


# noinspection PyUnusedLocal
@FallbackDescriptorGenerator.register_handler(LocalResponseNormalization)
def local_response_normalization(op: LocalResponseNormalization, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"local_response_normalization": source},
        "local_response_normalization",
        inputs=[memory_layout[x]],
        outputs=[memory_layout[y]],
        call_option={"out_spatial": [y.shape_dict[Axis.H], y.shape_dict[Axis.W]],
                     "n": x.shape_dict[Axis.N],
                     "out_size": y.shape_dict[Axis.C],
                     "strides_x": calculate_all_strides(x),
                     "strides_y": calculate_all_strides(y),
                     "p_half_n": int(op.parameters["n"] // 2),
                     "p_k": float(op.parameters["k"]),
                     "p_alpha": float(op.parameters["alpha"]),
                     "p_minus_beta": float(-op.parameters["beta"])}
    )

    return [kernel]
