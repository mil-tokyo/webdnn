import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn import Placeholder
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.placeholder_variable import PlaceholderVariable


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


def test_with_placeholder():
    link = chainer.links.Linear(16, 32)
    vx = chainer.Variable(np.random.rand(2, 16).astype(np.float32))
    vy = link(vx)

    N = Placeholder(label="N")
    px = PlaceholderVariable([N, 16])
    py = link(px)

    graph = ChainerConverter().convert([px], [py])

    N.value = 2
    generate_kernel_test_case(
        description=f"[chainer] L.Linear with placeholder",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={graph.inputs[0]: vx.data},
        expected={graph.outputs[0]: vy.data},
    )
