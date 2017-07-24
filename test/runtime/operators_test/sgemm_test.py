import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.backend.webassembly.operators.sgemm import Sgemm as WasmSgemm
from webdnn.backend.webgpu.operators.sgemm import Sgemm as WebGPUSgemm
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


@wrap_template
def template(transpose_A=False, transpose_B=False, description: str = ""):
    va = np.random.rand(5, 6)
    vb = np.random.rand(6, 7)

    vc = np.dot(va, vb)

    a = Variable((va if transpose_A else va.transpose()).shape, order=OrderNC)
    b = ConstantVariable((vb if transpose_B else vb.transpose()), order=OrderNC)
    c1, = WebGPUSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=transpose_A, transpose_B=transpose_B)(a, b)
    c2, = WasmSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=transpose_A, transpose_B=transpose_B)(a, b)

    generate_kernel_test_case(
        description=f"Sgemm {description}",
        backend="webgpu",
        graph=Graph([a], [c1]),
        inputs={a: (va if transpose_A else va.transpose())},
        expected={c1: vc}
    )
    generate_kernel_test_case(
        description=f"Sgemm {description}",
        backend="webassembly",
        graph=Graph([a], [c2]),
        inputs={a: (va if transpose_A else va.transpose())},
        expected={c2: vc}
    )


def test_NN():
    template(transpose_A=False, transpose_B=False)


def test_NT():
    template(transpose_A=False, transpose_B=True)


def test_TN():
    template(transpose_A=True, transpose_B=False)


def test_TT():
    template(transpose_A=True, transpose_B=True)
