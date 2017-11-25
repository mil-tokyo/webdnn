import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


@wrap_template
def template(a_shape=(2, 3, 4, 5), b_shape=(3, 4, 5, 6), axes=((1, 2, 3), (0, 1, 2)), backend=None, description: str = ""):
    va = np.random.rand(*a_shape).astype(np.float32)
    vb = np.random.rand(*b_shape).astype(np.float32)
    vc = np.tensordot(va, vb, axes)

    a = Variable(a_shape, Order([None] * len(a_shape)))
    b = Variable(b_shape, Order([None] * len(b_shape)))
    c, = Tensordot(None, axes=[[v.order.axes[aaa] for aaa in aa] for v, aa in zip([a, b], axes)])(a, b)

    generate_kernel_test_case(
        description=f"Tensordot {description}",
        backend=backend,
        graph=Graph([a, b], [c]),
        inputs={a: va, b: vb},
        expected={c: vc}
    )


def test():
    template()


def test_large():
    template(a_shape=(1024, 1024), b_shape=(1024, 1024), axes=((1,), (0,)), backend=["webgpu", "webgl", "webassembly"])


def test_vector_inner_product():
    template(a_shape=(1, 10), b_shape=(10, 1), axes=((1,), (0,)))


def test_vector_outer_product():
    template(a_shape=(10, 1), b_shape=(1, 10), axes=((1,), (0,)))


def test_NN():
    template(a_shape=(2, 10), b_shape=(10, 2), axes=((1,), (0,)))


def test_NT():
    template(a_shape=(2, 10), b_shape=(2, 10), axes=((1,), (1,)))


def test_TN():
    template(a_shape=(10, 2), b_shape=(10, 2), axes=((0,), (0,)))


def test_TT():
    template(a_shape=(10, 2), b_shape=(2, 10), axes=((0,), (1,)))
