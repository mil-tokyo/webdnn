import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(axis=1, description: str = ""):
    vx = chainer.Variable(np.random.rand(2, 5, 6, 8))
    vy = chainer.functions.crelu(vx, axis)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.crelu {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "fallback"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_axis_0():
    template(axis=0)
