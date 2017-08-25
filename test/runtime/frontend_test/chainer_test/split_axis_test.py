import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter


def test():
    vx = chainer.Variable(np.random.rand(2, 8, 6, 12))
    vy1, vy2, vy3 = chainer.functions.split_axis(vx, [4, 10], 3)

    graph = ChainerConverter().convert([vx], [vy1, vy2, vy3])

    x = graph.inputs[0]
    y1 = graph.outputs[0]
    y2 = graph.outputs[1]
    y3 = graph.outputs[2]

    generate_kernel_test_case(
        description=f"[chainer] F.SplitAxis",
        graph=graph,
        inputs={x: vx.data},
        backend=["webgpu", "webassembly", "fallback"],
        expected={
            y1: vy1.data,
            y2: vy2.data,
            y3: vy3.data
        },
    )
