from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.backend.fallback.kernels.util import calculate_stride
from webdnn.graph.axis import Axis
from webdnn.graph.operators.linear import Linear
from webdnn.graph.order import OrderNC

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
linear: function(input_arrays, output_arrays, option) {
var x = input_arrays[0];
var w = input_arrays[1];
var y = output_arrays[0];
var m = option.m | 0;
var n = option.n | 0;
var k = option.k | 0;
var x_k_stride = option.x_k_stride | 0;
var x_m_stride = option.x_m_stride | 0;
var w_k_stride = option.w_k_stride | 0;
var w_n_stride = option.w_n_stride | 0;

for (var i = 0; i < m; i++) {
  for (var j = 0; j < n; j++) {
    var sum = 0.0;
    for (var s = 0; s < k; s++) {
      sum += x[i * x_m_stride + s * x_k_stride] * w[s * w_k_stride + j * w_n_stride];
    }
    y[i * n + j] = sum;
  }
}

},


"""


# noinspection PyUnusedLocal
@FallbackDescriptorGenerator.register_handler(Linear)
def linear(op: Linear, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    w = op.inputs["w"]
    y = op.outputs["y"]

    assert y.order == OrderNC
    if x.order.ndim == 2:
        assert w.order.ndim == 2
        k = x.shape_dict[Axis.C]
        m = x.shape_dict[Axis.N]
        n = w.shape_dict[Axis.N]
        # 各行列操作方向でのstrideを求める
        # 操作軸の番号より右側にある(inner-loopの)次元の要素数の積
        x_k_stride = calculate_stride(x, Axis.C)
        x_m_stride = calculate_stride(x, Axis.N)
        w_k_stride = calculate_stride(w, Axis.C)
        w_n_stride = calculate_stride(w, Axis.N)
    elif x.order.ndim == 4:
        assert w.order.ndim == 4
        # CHWが、連続していてx,wで同順のみサポート(NCHW/NCHW, NHWC/HWCN, ...)
        x_order_wo_n = list(x.order.axes)
        x_order_wo_n.remove(Axis.N)  # [Axis.C, Axis.H, Axis.W]
        x_n_size = x.shape_dict[Axis.N]
        x_chw_size = x.size // x_n_size
        w_order_wo_n = list(w.order.axes)
        w_order_wo_n.remove(Axis.N)
        w_n_size = w.shape_dict[Axis.N]
        w_chw_size = w.size // w_n_size

        assert x_chw_size == w_chw_size
        assert x_order_wo_n == w_order_wo_n
        k = x_chw_size
        m = x_n_size
        n = w_n_size
        if x.order.axes[0] == Axis.N:
            # N***
            x_k_stride = 1
            x_m_stride = x_chw_size
        elif x.order.axes[3] == Axis.N:
            # ***N
            x_k_stride = x_n_size
            x_m_stride = 1
        else:
            # such as HWNC
            raise ValueError()
        if w.order.axes[0] == Axis.N:
            # N***
            w_k_stride = 1
            w_n_stride = w_chw_size
        elif w.order.axes[3] == Axis.N:
            # ***N
            w_k_stride = w_n_size
            w_n_stride = 1
        else:
            # such as HWNC
            raise ValueError()

    else:
        raise ValueError()

    kernel = Kernel(
        {"linear": source},
        "linear",
        inputs=[memory_layout[x], memory_layout[w]],
        outputs=[memory_layout[y]],
        call_option={"m": m,
                     "n": n,
                     "k": k,
                     "x_k_stride": x_k_stride,
                     "x_m_stride": x_m_stride,
                     "w_k_stride": w_k_stride,
                     "w_n_stride": w_n_stride}
    )

    return [kernel]
