import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(n=5, k=2.0, alpha=1e-4, beta=.75, description=""):
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
    vy = chainer.functions.local_response_normalization(vx, n=n, k=k, alpha=alpha, beta=beta)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.local_response_normalization {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "fallback"],
        inputs={x: vx.data},
        expected={y: vy.data}
    )


def test():
    template()


def test_n():
    template(n=4)


def test_k():
    template(k=3.5)


def test_alpha():
    template(alpha=1e-2)


def test_beta():
    template(beta=0.5)


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(1, 3, 16, 16).astype(np.float32))
    vy = chainer.functions.local_response_normalization(vx)

    N = Placeholder(label="N")
    C = Placeholder(label="C")
    H = Placeholder(label="H")
    W = Placeholder(label="W")
    px = PlaceholderVariable([N, C, H, W])
    py = chainer.functions.local_response_normalization(px)

    graph = ChainerConverter().convert([px], [py])

    x = graph.inputs[0]
    y = graph.outputs[0]

    N.value = 1
    C.value = 3
    H.value = 16
    W.value = 16
    generate_kernel_test_case(
        description=f"[chainer] F.local_response_normalization with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )
