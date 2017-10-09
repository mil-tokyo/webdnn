import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.graph import Graph
from webdnn.graph.operators.sgemm import Sgemm
from webdnn.graph.order import OrderNC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


@wrap_template
def template(transpose_A=False, transpose_B=False, M=5, N=8, K=6, description: str = ""):
    va = np.random.rand(M, K).astype(np.float32)
    vb = np.random.rand(K, N).astype(np.float32)
    va[0, :] = 2
    vb[:, 0] = 2

    vc = np.dot(va, vb)

    a = Variable((va if transpose_A else va.transpose()).shape, order=OrderNC)
    b = ConstantVariable((vb if transpose_B else vb.transpose()), order=OrderNC)
    c, = Sgemm(None, M=M, N=N, K=K, out_shape=[M, N], out_order=OrderNC, transpose_A=transpose_A, transpose_B=transpose_B)(a, b)
    generate_kernel_test_case(
        description=f"Sgemm {description}",
        backend=["webgpu", "webassembly", "webgl"],
        graph=Graph([a], [c]),
        inputs={a: (va if transpose_A else va.transpose())},
        expected={c: vc}
    )


def test_large():
    template(M=1024, N=1024, K=1024, transpose_A=True, transpose_B=True)


def test_vector_inner_product():
    template(M=10, N=20, K=1, transpose_A=True, transpose_B=True)


def test_vector_outer_product():
    template(M=1, N=1, K=20, transpose_A=True, transpose_B=True)


def test_NN():
    template(transpose_A=False, transpose_B=False)


def test_NN_large():
    template(transpose_A=False, transpose_B=False, M=100, N=100, K=100)


def test_NT():
    template(transpose_A=False, transpose_B=True)


def test_TN():
    template(transpose_A=True, transpose_B=False)


def test_TT():
    template(transpose_A=True, transpose_B=True)
