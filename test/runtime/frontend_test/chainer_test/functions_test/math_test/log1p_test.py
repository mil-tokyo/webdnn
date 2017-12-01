import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter


@wrap_template
def template(description: str = ""):
    # NOTE:
    # In WebDNN, log1p(x) is converted into log(1+x), which is not as accurate in case x is so small that
    # 1+x == 1 in floating point accuracy.
    vx = chainer.Variable(np.random.rand(2, 5, 6, 8).astype(np.float32) + 1)
    vy = chainer.functions.log1p(vx)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.log1p {description}",
        graph=graph,
        inputs={x: vx.data},
        expected={y: vy.data},
        EPS=1e-2
    )


def test():
    template()
