import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, y_shape, description: str = ""):
    vx = np.random.rand(*x_shape)
    vy = np.reshape(vx, [x if y == 0 else y for x, y in zip(x_shape, y_shape)])

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)
    operator = make_node("Reshape", ["x"], ["y"], shape=y_shape)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    assert list(vy.shape) == list(graph.outputs[0].shape)

    generate_kernel_test_case(
        description=f"[ONNX] Reshape {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 3, 4, 5], y_shape=[4, 5, 3, 2])


def test_change_dim():
    template(x_shape=[2, 3, 4, 5], y_shape=[8, 5, 3])


def test_wildcard():
    template(x_shape=[2, 3, 4, 5], y_shape=[4, 5, -1, 2])


def test_no_change():
    template(x_shape=[2, 3, 4, 5], y_shape=[0, 0, 0, 5])


def test_flatten():
    template(x_shape=[2, 3, 4, 5], y_shape=[0, -1])
