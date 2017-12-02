import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, axis, description: str = ""):
    vx = np.random.rand(*x_shape) - 0.5
    vy = np.exp(vx) / np.sum(np.exp(vx), axis=axis, keepdims=True)

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)
    operator = make_node("Softmax", ["x"], ["y"], axis=axis)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] Softmax {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 3, 4, 5], axis=1)


def test_most_inner_axis():
    template(x_shape=[2, 3, 4, 5], axis=3)


def test_most_outer_axis():
    template(x_shape=[2, 3, 4, 5], axis=0)
