import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, alpha, gamma, description: str = ""):
    np_alpha = 1.6732 if alpha is None else alpha
    np_gamma = 1.0507 if gamma is None else gamma
    vx = np.random.rand(*x_shape) - 0.5

    vy = vx.copy()
    vy[vx <= 0] = np_gamma * (np_alpha * np.exp(vx[vx <= 0]) - np_alpha)
    vy[vx > 0] = np_gamma * vx[vx > 0]

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)

    kwargs = {}
    if alpha is not None:
        kwargs["alpha"] = alpha
    if gamma is not None:
        kwargs["gamma"] = gamma
    operator = make_node("Selu", ["x"], ["y"], **kwargs)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] Selu {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
        EPS=1e-2
    )


def test():
    template(x_shape=[2, 3, 4, 5], alpha=None, gamma=None)


def test_alpha():
    template(x_shape=[2, 3, 4, 5], alpha=2.0, gamma=None)


def test_beta():
    template(x_shape=[2, 3, 4, 5], alpha=None, gamma=2.0)
