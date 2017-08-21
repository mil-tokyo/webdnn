import itertools

import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_general():
    vx = np.random.rand(2, 4, 6, 8)
    vy = np.empty((2, 2, 3, 8))
    KH, KW = (2, 2)
    SH, SW = (2, 2)
    PH, PW = (0, 0)

    for n, h2, w2, c in itertools.product(range(vy.shape[0]),
                                          range(vy.shape[1]),
                                          range(vy.shape[2]),
                                          range(vy.shape[3])):
        v = 0
        for (kh, kw) in itertools.product(range(KH), range(KW)):
            h1 = (h2 * SH - PH) + kh
            w1 = (w2 * SW - PW) + kw

            v += 0 if (h1 < 0 or h1 >= 4 or w1 < 0 or w1 >= 6) else vx[n, h1, w1, c]

        vy[n, h2, w2, c] = v / (KH * KW)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = AveragePooling2D(None, ksize=(KH, KW), stride=(SH, SW), padding=(PH, PW))(x)

    generate_kernel_test_case(
        description=f"Average Pooling",
        backend=["webgpu", "webgl", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )


def test_irregular_size():
    vx = np.random.rand(2, 4, 6, 8)
    vy = np.empty((2, 4, 5, 8))
    KH, KW = (3, 4)
    SH, SW = (1, 2)
    PH, PW = (1, 3)

    for n, h2, w2, c in itertools.product(range(vy.shape[0]),
                                          range(vy.shape[1]),
                                          range(vy.shape[2]),
                                          range(vy.shape[3])):
        v = 0
        for (kh, kw) in itertools.product(range(KH), range(KW)):
            h1 = (h2 * SH - PH) + kh
            w1 = (w2 * SW - PW) + kw

            v += 0 if (h1 < 0 or h1 >= 4 or w1 < 0 or w1 >= 6) else vx[n, h1, w1, c]

        vy[n, h2, w2, c] = v / (KH * KW)

    x = Variable(vx.shape, order=OrderNHWC)
    y, = AveragePooling2D(None, ksize=(KH, KW), stride=(SH, SW), padding=(PH, PW))(x)

    generate_kernel_test_case(
        description=f"Average Pooling with irregular window size",
        backend=["webgpu", "webgl", "webassembly", "fallback"],
        graph=Graph([x], [y]),
        inputs={x: vx},
        expected={y: vy}
    )
