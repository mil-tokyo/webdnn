from typing import List, Type
import numpy as np

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.backend.fallback.kernels.util import calculate_stride
from graph_builder.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA

# x: (batch_size, h, w, in_size), w: (kh, kw, in_size, out_size), y: (batch_size, oh, ow, out_size) C-order
# EcmaScript3 to support older browsers
source = """
max_pooling_2d: function(input_arrays, output_arrays, param_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var n = option.n | 0;
var in_spatial = option.in_spatial;
var out_spatial = option.out_spatial;
var out_size = option.out_size | 0;
var in_size = option.in_size | 0;
var padding = option.padding;
var stride = option.stride;
var ksize = option.ksize;
var strides_x = option.strides_x;
var strides_w = option.strides_w;
var strides_y = option.strides_y;

var get_x = function(n_, y_, x_, c_) {
  y_ -= padding[0];
  x_ -= padding[1];
  if (y_ < 0 || y_ >= in_spatial[0] || x_ < 0 || x_ >= in_spatial[1]) {
    return -Infinity;
  }
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
        var window_max = -Infinity;
        for (var ky = 0; ky < ksize[0]; ky++) {
          for (var kx = 0; kx < ksize[1]; kx++) {
            for (var ic = 0; ic < in_size; ic++) {
              var val = get_x(batch, oy * stride[0] + ky, ox * stride[1] + kx, ic);
              if (val > window_max) {
                window_max = val;
              }
            }
          }
        }
        set_y(batch, oy, ox, oc, window_max);
      }
    }
  }
}

},

"""


def calculate_all_strides(var):
    return [calculate_stride(var, axis) for axis in [A.Axis.N, A.Axis.H, A.Axis.W, A.Axis.C]]


def max_pooling_2d(op: Operator) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"max_pooling_2d": source},
        "max_pooling_2d",
        inputs=[x.parameters["name"]],
        outputs=[y.parameters["name"]],
        weights=[],
        call_option={"in_spatial": [x.shape_dict[A.Axis.H], x.shape_dict[A.Axis.W]],
                     "n": x.shape_dict[A.Axis.N],
                     "out_size": y.shape_dict[A.Axis.C],
                     "out_spatial": [y.shape_dict[A.Axis.H], y.shape_dict[A.Axis.W]],
                     "strides_x": calculate_all_strides(x),
                     "strides_y": calculate_all_strides(y),
                     "padding": op.parameters["padding"],
                     "stride": op.parameters["stride"],
                     "ksize": op.parameters["ksize"]}
    )

    return [kernel]
