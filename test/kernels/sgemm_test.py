import numpy as np

from test.util import generate_kernel_test_case
from webdnn.backend.webassembly.operators.sgemm import Sgemm as WasmSgemm
from webdnn.backend.webgpu.operators.sgemm import Sgemm as WebGPUSgemm
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_NN():
    va = np.random.rand(6, 5)
    vb = np.random.rand(7, 6)
    vc = np.dot(va.transpose(), vb.transpose())

    a = Variable(va.shape, order=OrderNC)
    b = ConstantVariable(vb, order=OrderNC)
    c1, = WebGPUSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=False, transpose_B=False)(a, b)
    c2, = WasmSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=False, transpose_B=False)(a, b)

    generate_kernel_test_case(
        description=f"Sgemm: NN",
        backend="webgpu",
        graph=Graph([a], [c1]),
        inputs={a: va},
        expected={c1: vc}
    )
    generate_kernel_test_case(
        description=f"Sgemm: NN",
        backend="webassembly",
        graph=Graph([a], [c2]),
        inputs={a: va},
        expected={c2: vc}
    )


def test_TN():
    va = np.random.rand(5, 6)
    vb = np.random.rand(7, 6)
    vc = np.dot(va, vb.transpose())

    a = Variable(va.shape, order=OrderNC)
    b = ConstantVariable(vb, order=OrderNC)
    c1, = WebGPUSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=True, transpose_B=False)(a, b)
    c2, = WasmSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=True, transpose_B=False)(a, b)

    generate_kernel_test_case(
        description=f"Sgemm: TN",
        backend="webgpu",
        graph=Graph([a], [c1]),
        inputs={a: va},
        expected={c1: vc}
    )
    generate_kernel_test_case(
        description=f"Sgemm: TN",
        backend="webassembly",
        graph=Graph([a], [c2]),
        inputs={a: va},
        expected={c2: vc}
    )


def test_NT():
    va = np.random.rand(6, 5)
    vb = np.random.rand(6, 7)
    vc = np.dot(va.transpose(), vb)

    a = Variable(va.shape, order=OrderNC)
    b = ConstantVariable(vb, order=OrderNC)
    c1, = WebGPUSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=False, transpose_B=True)(a, b)
    c2, = WasmSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=False, transpose_B=True)(a, b)

    generate_kernel_test_case(
        description=f"Sgemm: NT",
        backend="webgpu",
        graph=Graph([a], [c1]),
        inputs={a: va},
        expected={c1: vc}
    )
    generate_kernel_test_case(
        description=f"Sgemm: NT",
        backend="webassembly",
        graph=Graph([a], [c2]),
        inputs={a: va},
        expected={c2: vc}
    )


def test_TT():
    va = np.random.rand(5, 6)
    vb = np.random.rand(6, 7)
    vc = np.dot(va, vb)

    a = Variable(va.shape, order=OrderNC)
    b = ConstantVariable(vb, order=OrderNC)
    c1, = WebGPUSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=True, transpose_B=True)(a, b)
    c2, = WasmSgemm(None, M=5, N=7, K=6, out_shape=[5, 7], out_order=OrderNC, transpose_A=True, transpose_B=True)(a, b)

    generate_kernel_test_case(
        description=f"Sgemm: TT",
        backend="webgpu",
        graph=Graph([a], [c1]),
        inputs={a: va},
        expected={c1: vc}
    )
    generate_kernel_test_case(
        description=f"Sgemm: TT",
        backend="webassembly",
        graph=Graph([a], [c2]),
        inputs={a: va},
        expected={c2: vc}
    )
