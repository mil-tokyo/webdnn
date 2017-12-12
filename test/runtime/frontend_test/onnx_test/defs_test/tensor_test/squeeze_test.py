import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, axes, description: str = ""):
    vx = np.random.rand(*x_shape)
    vy = np.squeeze(vx, tuple(axes))

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)
    operator = make_node("Squeeze", ["x"], ["y"], axes=axes)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    assert list(vy.shape) == list(graph.outputs[0].shape)

    generate_kernel_test_case(
        description=f"[ONNX] Squeeze {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[1, 3, 1, 5, 1], axes=[0, 2, 4])


def test_remain_some_axes():
    template(x_shape=[1, 3, 1, 5, 1], axes=[0, 4])


def test_remain_some_axes2():
    template(x_shape=[1, 3, 1, 5, 1], axes=[0])


def test_remain_some_axes3():
    template(x_shape=[3, 1, 1, 1, 5], axes=[2])


def test_remain_some_axes4():
    template(x_shape=[3, 1, 1, 5], axes=[2])
