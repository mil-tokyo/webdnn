import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(r=2, description=""):
    vx = chainer.Variable(np.random.rand(2, 4 * r * r, 6, 8).astype(np.float32))
    vy = chainer.functions.depth2space(vx, r)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Depth2Space {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_r_3():
    template(r=3)
