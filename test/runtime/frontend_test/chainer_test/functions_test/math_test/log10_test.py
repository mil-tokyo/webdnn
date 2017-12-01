import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(description: str = ""):
    vx = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32))
    vy = chainer.functions.log10(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.log10 {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
    )


def test():
    template()
