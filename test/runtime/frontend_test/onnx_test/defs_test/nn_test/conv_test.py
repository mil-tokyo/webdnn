import chainer
import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(N=2, H=5, W=5, Cin=7, Cout=9, KH=3, KW=3, SH=1, SW=1, PH=1, PW=1, DH=1, DW=1, use_bias=False, description: str = ""):
    x_shape = [N, Cin, H, W]
    w_shape = [Cout, Cin, KH, KW]

    vx = np.random.rand(*x_shape)
    vw = np.random.rand(*w_shape)
    vb = np.random.rand(Cout) if use_bias else None

    if DH != 1 or DW != 1:
        vy = chainer.functions.dilated_convolution_2d(vx, vw, b=vb, stride=[SH, SW], pad=[PH, PW], dilate=[DH, DW]).data
    else:
        vy = chainer.functions.convolution_2d(vx, vw, b=vb, stride=[SH, SW], pad=[PH, PW]).data

    x = make_tensor_value_info("x", x_shape)
    w = make_tensor_value_info("w", w_shape)
    y = make_tensor_value_info("y", vy.shape)

    kwargs = {
        "kernel_shape": [KH, KW],
        "strides": [SH, SW],
        "dilations": [DH, DW],
        "pads": [PH, PH, PW, PW]
    }
    if use_bias:
        b = make_tensor_value_info("b", vb.shape)
        operator = make_node("Conv", ["x", "w", "b"], ["y"], **kwargs)
        model = make_model([operator], [x, w, b], [y])

    else:
        operator = make_node("Conv", ["x", "w"], ["y"], **kwargs)
        model = make_model([operator], [x, w], [y])

    graph = ONNXConverter().convert(model)

    inputs = {
        graph.inputs[0]: vx,
        graph.inputs[1]: vw
    }

    if use_bias:
        inputs[graph.inputs[2]] = vb

    generate_kernel_test_case(
        description=f"[ONNX] Conv {description}",
        graph=graph,
        inputs=inputs,
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_projection():
    template(KH=1, KW=1, SH=1, SW=1, PH=0, PW=0)


def test_global_conv():
    template(KH=5, KW=5, SH=1, SW=1, PH=0, PW=0)


def test_odd_k():
    template(KH=3, KW=5)


def test_odd_s():
    template(SH=1, SW=2)


def test_odd_p():
    template(PH=0, PW=0)


def test_dilation():
    template(DH=2, DW=2)


def test_with_bias():
    template(use_bias=True)
