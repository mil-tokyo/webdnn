import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.placeholder import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


@wrap_template
def template(eps=1e-5, axis=1, description=""):
    vx = chainer.Variable(np.random.rand(2, 4).astype(np.float32))
    vy = chainer.functions.normalize(vx, eps=eps, axis=axis)

    graph = ChainerConverter().convert([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.normalize {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "fallback"],
        inputs={x: vx.data},
        expected={y: vy.data}
    )


def test():
    template()


def test_eps():
    template(eps=1e-1)


def test_with_placeholder():
    vx = chainer.Variable(np.random.rand(1, 8).astype(np.float32))
    vy = chainer.functions.normalize(vx)

    N = Placeholder(label="N")
    C = Placeholder(label="C")
    px = PlaceholderVariable([N, C])
    py = chainer.functions.normalize(px)

    graph = ChainerConverter().convert([px], [py])

    x = graph.inputs[0]
    y = graph.outputs[0]

    N.value = 1
    C.value = 8
    generate_kernel_test_case(
        description=f"[chainer] F.normalize with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={x: vx.data},
        expected={y: vy.data},
    )
