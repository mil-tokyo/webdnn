from typing import List

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.graph import Operator
from graph_builder.graph.operators import attributes as A

# x: (batch_size, h, w, in_size), w: (kh, kw, in_size, out_size), y: (batch_size, oh, ow, out_size) C-order
# EcmaScript3 to support older browsers
source = """
convolution_2d: function(input_arrays, output_arrays, param_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var w = param_arrays[0];
var n = option.n | 0;
var in_spatial = option.in_spatial;
var out_spatial = option.out_spatial;
var out_size = option.out_size | 0;
var in_size = option.in_size | 0;
var pad = option.pad;
var stride = option.stride;
var ksize = option.ksize;

var get_x = function(n_, y_, x_, c_) {
  y_ -= pad[0];
  x_ -= pad[1];
  if (y_ < 0 || y_ >= in_spatial[0] || x_ < 0 || x_ >= in_spatial[1]) {
    return 0.0;
  }
  var idx = (((n_ * in_spatial[0]) + y_) * in_spatial[1] + x_) * in_size + c_;
  return x[idx];
};

var get_w = function(ky_, kx_, in_c, out_c) {
  var idx = (((ky_ * ksize[1]) + kx_) * in_size + in_c) * out_size + out_c;
  return w[idx];
};

var set_y = function(n_, y_, x_, c_, val) {
  var idx = (((n_ * out_spatial[0]) + y_) * out_spatial[1] + x_) * out_size + c_;
  y[idx] = val;
};

for (var batch = 0; batch < n; batch++) {
  for (var oy = 0; oy < out_spatial[0]; oy++) {
    for (var ox = 0; ox < out_spatial[1]; ox++) {
      for (var oc = 0; oc < out_size; oc++) {
        var sum = 0.0;
        for (var ky = 0; ky < ksize[0]; ky++) {
          for (var kx = 0; kx < ksize[1]; kx++) {
            for (var ic = 0; ic < in_size; ic++) {
              sum += get_x(batch, oy * stride[0] + ky, ox * stride[1] + kx, ic) * get_w(ky, kx, ic, oc);
            }
          }
        }
        set_y(batch, oy, ox, oc, sum);
      }
    }
  }
}

},

"""


def convolution_2d(op: Operator) -> List[Kernel]:
    x = op.inputs["x"]
    w = op.inputs["w"]
    y = op.outputs["y"]

    assert x.ndim == 4

    kernel = Kernel(
        {"convolution_2d": source},
        "convolution_2d",
        inputs=[x.parameters["name"]],
        outputs=[y.parameters["name"]],
        weights=[w.parameters["name"]],
        call_option={"in_spatial": [x.shape_dict[A.Axis.H], x.shape_dict[A.Axis.W]],
                     "n": x.shape_dict[A.Axis.N],
                     "out_size": y.shape_dict[A.Axis.C],
                     "in_size": x.shape_dict[A.Axis.C],
                     "out_spatial": [y.shape_dict[A.Axis.H], y.shape_dict[A.Axis.W]],
                     "pad": op.parameters["pad"],
                     "stride": op.parameters["stride"],
                     "ksize": op.parameters["ksize"]}
    )

    return [kernel]
