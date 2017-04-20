from typing import List
import numpy as np

from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.graph import Operator
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA

# assume (batch_size, in_size) * (in_size, out_size) = (batch_size, out_size), C-order
# EcmaScript3 to support older browsers

source = """
linear: function(input_arrays, output_arrays, param_arrays, option) {
var x = input_arrays[0];
var y = output_arrays[0];
var w = param_arrays[0];
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


def linear(op: Operator) -> List[Kernel]:
    x = op.inputs["x"]
    w = op.inputs["w"]
    y = op.outputs["y"]

    assert y.axis_order is VA.OrderNC
    if x.axis_order.ndim == 2:
        assert w.axis_order.ndim == 2
        k = x.shape_dict[A.Axis.C]
        m = x.shape_dict[A.Axis.N]
        n = w.shape_dict[A.Axis.N]
        # 各行列操作方向でのstrideを求める
        # 操作軸の番号より右側にある(inner-loopの)次元の要素数の積
        x_k_stride = int(np.prod(x.shape[x.axis_order.axes_dict[A.Axis.C]+1:]))
        x_m_stride = int(np.prod(x.shape[x.axis_order.axes_dict[A.Axis.N]+1:]))
        w_k_stride = int(np.prod(w.shape[w.axis_order.axes_dict[A.Axis.C]+1:]))
        w_n_stride = int(np.prod(w.shape[w.axis_order.axes_dict[A.Axis.N]+1:]))
    elif x.axis_order.ndim == 4:
        assert w.axis_order.ndim == 4
        # CHWが、連続していてx,wで同順のみサポート(NCHW/NCHW, NHWC/HWCN, ...)
        x_order_wo_n = list(x.axis_order.axes)
        x_order_wo_n.remove(A.Axis.N)  # [A.Axis.C, A.Axis.H, A.Axis.W]
        x_chw_size = int(np.prod([x.shape_dict[axis] for axis in x_order_wo_n]))
        x_n_size = x.shape_dict[A.Axis.N]
        w_order_wo_n = list(w.axis_order.axes)
        w_order_wo_n.remove(A.Axis.N)
        w_chw_size = int(np.prod([w.shape_dict[axis] for axis in x_order_wo_n]))
        w_n_size = w.shape_dict[A.Axis.N]

        assert x_chw_size == w_chw_size
        assert x_order_wo_n == w_order_wo_n
        k = x_chw_size
        m = x_n_size
        n = w_n_size
        if x.axis_order.axes[0] == A.Axis.N:
            # N***
            x_k_stride = 1
            x_m_stride = x_chw_size
        elif x.axis_order.axes[3] == A.Axis.N:
            # ***N
            x_k_stride = x_n_size
            x_m_stride = 1
        else:
            # such as HWNC
            raise ValueError()
        if w.axis_order.axes[0] == A.Axis.N:
            # N***
            w_k_stride = 1
            w_n_stride = w_chw_size
        elif w.axis_order.axes[3] == A.Axis.N:
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
        inputs=[x.parameters["name"]],
        outputs=[y.parameters["name"]],
        weights=[w.parameters["name"]],
        call_option={"m": m,
                     "n": n,
                     "k": k,
                     "x_k_stride": x_k_stride,
                     "x_m_stride": x_m_stride,
                     "w_k_stride": w_k_stride,
                     "w_n_stride": w_n_stride}
    )

    return [kernel]
