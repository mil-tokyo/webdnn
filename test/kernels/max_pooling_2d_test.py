import itertools

import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    vx = np.random.rand(2, 4, 6, 8)
    vy = np.empty((2, 3, 4, 8))

    for n, h2, w2, c in itertools.product(range(vy.shape[0]),
                                          range(vy.shape[1]),
                                          range(vy.shape[2]),
                                          range(vy.shape[3])):
        v = -float("Infinity")
        for (kh, kw) in itertools.product(range(3), range(3)):
            h1 = (h2 * 2 - 1) + kh
            w1 = (w2 * 2 - 1) + kw

            v = max(v, 0 if (h1 < 0 or h1 >= 4 or w1 < 0 or w1 >= 6) else vx[n, h1, w1, c])

        vy[n, h2, w2, c] = v

    x = Variable(vx.shape, order=OrderNHWC)
    y, = MaxPooling2D(None, ksize=3, padding=1, stride=2)(x)

    generate_kernel_test_case(
        description=f"Max Pooling",
        backend=["webgpu", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
