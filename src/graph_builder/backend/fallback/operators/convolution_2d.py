from typing import List

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.backend.fallback.operators.operator import Operator

# x: (batch_size, h, w, in_size), w: (kh, kw, in_size, out_size), y: (batch_size, oh, ow, out_size) C-order
# EcmaScript3 to support older browsers
convolution_2d_source = """
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


#  same as Chainer
def get_conv_outsize(size, k, s, p, cover_all=False, d=1):
    dk = k + (k - 1) * (d - 1)
    if cover_all:
        return (size + p * 2 - dk + s - 1) // s + 1
    else:
        return (size + p * 2 - dk) // s + 1


class Convolution2D(Operator):
    name: str = "convolution_2d"

    def convert_to_kernels(self,
                           batch_size: int) -> List[Kernel]:
        source = convolution_2d_source
        input_shape = self.inputs[0].shape
        assert len(input_shape) == 4
        params = self.layer.parameters
        out_sp = []
        for dim in [0, 1]:
            out_sp.append(get_conv_outsize(input_shape[1 + dim],
                                           params["ksize"][dim], params["stride"][dim], params["pad"][dim],
                                           params["cover_all"]))

        kernel = Kernel(
            {self.name: source},
            self.name,
            inputs=[v.name for v in self.inputs],
            outputs=[v.name for v in self.outputs],
            weights=[self.layer.name + "/W"],
            call_option={"in_spatial": input_shape[1:3],
                         "n": input_shape[0],
                         "out_size": params["out_size"],
                         "in_size": params["in_size"],
                         "out_spatial": out_sp,
                         "pad": params["pad"],
                         "stride": params["stride"],
                         "ksize": params["ksize"]}
        )

        return [kernel]
