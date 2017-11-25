import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(nobias=False, description=""):
    link = chainer.links.Linear(6, 8, nobias=nobias)

    vx = chainer.Variable(np.random.rand(4, 6).astype(np.float32))
    vy = link(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.Linear {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()


def test_nobias():
    template(nobias=True)
