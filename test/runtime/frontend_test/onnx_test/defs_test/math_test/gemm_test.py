import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(M=5, K=6, N=7, c_shape=None, transA=False, transB=False, broadcast=False, alpha=1.0, beta=0.0,
             description: str = ""):
    if c_shape is None:
        c_shape = [M, N]

    va = np.random.rand(*((K, M) if transA else (M, K)))
    vb = np.random.rand(*((N, K) if transB else (K, N)))
    vc = np.random.rand(*c_shape)
    vd = (va.T if transA else va) @ (vb.T if transB else vb) * alpha + vc * beta

    kwargs = {
        "broadcast": broadcast,
        "transA": transA,
        "transB": transB,
        "alpha": alpha,
        "beta": beta
    }

    a = make_tensor_value_info("a", va.shape)
    b = make_tensor_value_info("b", vb.shape)
    c = make_tensor_value_info("c", vc.shape)
    d = make_tensor_value_info("d", vd.shape)

    operator = make_node("Gemm", ["a", "b", "c"], ["d"], **kwargs)
    model = make_model([operator], [a, b, c], [d])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] Gemm {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: va,
            graph.inputs[1]: vb,
            graph.inputs[2]: vc
        },
        expected={graph.outputs[0]: vd},
    )


def test_NN():
    template()


def test_NT():
    template(transB=True)


def test_TN():
    template(transA=True)


def test_TT():
    template(transA=True, transB=True)


def test_alpha():
    template(alpha=2.0)


def test_beta():
    template(beta=2.0)


def test_broadcast():
    template(M=5, K=6, N=7, broadcast=True, c_shape=[5, 1])
