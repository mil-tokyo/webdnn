import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


def test():
    vx = chainer.Variable(np.random.rand(2, 8, 6, 12).astype(np.float32))
    vy1, vy2, vy3 = chainer.functions.split_axis(vx, [4, 10], 3)

    graph = ChainerConverter().convert([vx], [vy1, vy2, vy3])

    x = graph.inputs[0]
    y1 = graph.outputs[0]
    y2 = graph.outputs[1]
    y3 = graph.outputs[2]

    generate_kernel_test_case(
        description=f"[chainer] F.split_axis",
        graph=graph,
        inputs={x: vx.data},
        expected={
            y1: vy1.data,
            y2: vy2.data,
            y3: vy3.data
        },
    )


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(2, 20, 4, 5).astype(np.float32))
    vy1, vy2, vy3 = chainer.functions.split_axis(vx, [5, 15], 1)

    N = Placeholder(label="N")
    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px = PlaceholderVariable([N, 20, H, W])
    py1, py2, py3 = chainer.functions.split_axis(px, [5, 15], 1)

    graph = ChainerConverter().convert([px], [py1, py2, py3])

    N.value = 2
    H.value = 4
    W.value = 5
    generate_kernel_test_case(
        description=f"[chainer] F.split_axis with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={
            graph.outputs[0]: vy1.data,
            graph.outputs[1]: vy2.data,
            graph.outputs[2]: vy3.data
        },
    )
