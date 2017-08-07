import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(alpha=1.0, description: str = ""):
    vx = chainer.Variable(np.random.rand(2, 5, 6, 8))
    vy = chainer.functions.elu(vx, alpha=alpha)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.elu {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_alpha():
    template(alpha=0.5)


def test_alpha_0():
    template(alpha=0)
