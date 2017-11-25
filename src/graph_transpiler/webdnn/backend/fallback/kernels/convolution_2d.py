from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.convolution2d import Convolution2D

# x: (batch_size, h, w, in_size), w: (kh, kw, in_size, out_size), y: (batch_size, oh, ow, out_size) C-order
# EcmaScript3 to support older browsers
source = """
convolution_2d: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var w = input_arrays[1];
var y = output_arrays[0];
var n = option.n | 0;
var in_spatial = option.in_spatial;
var out_spatial = option.out_spatial;
var out_size = option.out_size | 0;
var in_size = option.in_size | 0;
var padding = option.padding;
var stride = option.stride;
var ksize = option.ksize;
var dilation_rate = option.dilation_rate;
var strides_x = option.strides_x;
var strides_w = option.strides_w;
var strides_y = option.strides_y;

var get_x = function(n_, y_, x_, c_) {
  y_ -= padding[0];
  x_ -= padding[1];
  if (y_ < 0 || y_ >= in_spatial[0] || x_ < 0 || x_ >= in_spatial[1]) {
    return 0.0;
  }
  var idx = n_ * strides_x[0] + y_ * strides_x[1] + x_ * strides_x[2] + c_ * strides_x[3];
  return x[idx];
};

var get_w = function(ky_, kx_, in_c, out_c) {
  var idx = out_c * strides_w[0] + ky_ * strides_w[1] + kx_ * strides_w[2] + in_c * strides_w[3];
  return w[idx];
};

var set_y = function(n_, y_, x_, c_, val) {
  var idx = n_ * strides_y[0] + y_ * strides_y[1] + x_ * strides_y[2] + c_ * strides_y[3];
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
              sum += get_x(batch, oy * stride[0] + ky * dilation_rate[0],
                           ox * stride[1] + kx * dilation_rate[1],
                           ic) *
                     get_w(ky, kx, ic, oc);
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


@FallbackDescriptorGenerator.register_handler(Convolution2D)
def convolution_2d(op: Convolution2D, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    w = op.inputs["w"]
    y = op.outputs["y"]

    kernel = Kernel(
        {"convolution_2d": source},
        "convolution_2d",
        inputs=[memory_layout[x], memory_layout[w]],
        outputs=[memory_layout[y]],
        call_option={"in_spatial": [x.shape_dict[Axis.H], x.shape_dict[Axis.W]],
                     "n": x.shape_dict[Axis.N],
                     "out_size": y.shape_dict[Axis.C],
                     "in_size": x.shape_dict[Axis.C],
                     "out_spatial": [y.shape_dict[Axis.H], y.shape_dict[Axis.W]],
                     "strides_x": [x.stride_dict[a] for a in [Axis.N, Axis.H, Axis.W, Axis.C]],
                     "strides_w": [w.stride_dict[a] for a in [Axis.N, Axis.KH, Axis.KW, Axis.C]],
                     "strides_y": [y.stride_dict[a] for a in [Axis.N, Axis.H, Axis.W, Axis.C]],
                     "padding": op.padding,
                     "stride": op.stride,
                     "ksize": op.ksize,
                     "dilation_rate": op.dilation_rate}
    )

    return [kernel]
