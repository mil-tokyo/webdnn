import chainer
import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(N=2, H=5, W=5, C=7, KH=3, KW=3, SH=1, SW=1, PH=1, PW=1, DH=1, DW=1, description: str = ""):
    if DH != 1 or DW != 1:
        raise NotImplementedError

    x_shape = [N, C, H, W]

    vx = np.random.rand(*x_shape)
    vy = chainer.functions.average_pooling_2d(vx, ksize=[KH, KW], stride=[SH, SW], pad=[PH, PW]).data

    x = make_tensor_value_info("x", x_shape)
    y = make_tensor_value_info("y", vy.shape)

    kwargs = {
        "kernel_shape": [KH, KW],
        "strides": [SH, SW],
        "dilations": [DH, DW],
        "pads": [PH, PH, PW, PW]
    }
    operator = make_node("AveragePool", ["x"], ["y"], **kwargs)
    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] AveragePool {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_projection():
    template(KH=1, KW=1, SH=1, SW=1, PH=0, PW=0)


def test_global_pool():
    template(KH=5, KW=5, SH=1, SW=1, PH=0, PW=0)


def test_odd_k():
    template(KH=3, KW=5)


def test_odd_s():
    template(SH=1, SW=2)


def test_odd_p():
    template(PH=0, PW=0)
