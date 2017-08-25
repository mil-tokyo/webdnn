import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.order import OrderC, OrderNHWC, OrderNCHW, OrderCNHW
from webdnn.graph.variable import Variable


def test_major_axis():
    vx = np.random.rand(10, 6, 4, 8)
    n = 5
    k = 2
    alpha = 1e-4
    beta = 0.75

    np_axis = 3
    vx_squared = vx ** 2.0
    vx_scales = []
    for i in range(vx.shape[np_axis]):
        # if axis == 2: vx_squared[:, :, i-n//2:i+n//2+1, :]
        channel_slice = [slice(None)] * np_axis + \
                        [slice(max(0, i - n // 2), min(i + n // 2 + 1, vx.shape[np_axis]))] + \
                        [slice(None)] * (vx.ndim - np_axis - 1)
        vx_scales.append(np.sum(vx_squared[channel_slice], axis=np_axis, keepdims=True))
    vx_scale = (np.concatenate(vx_scales, axis=np_axis) * alpha + k) ** (-beta)
    vy = vx * vx_scale

    x = Variable(vx.shape, order=OrderNHWC)
    y, = LocalResponseNormalization(None, n=n, k=k, alpha=alpha, beta=beta)(x)

    generate_kernel_test_case(
        description=f"LocalResponseNormalization for major axis",
        backend=["webgpu", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
