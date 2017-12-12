import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, axis, kwargs, description: str = ""):
    vx = np.random.rand(*x_shape)
    y_shape = [np.product(vx.shape[:axis]), np.product(vx.shape[axis:])]
    vy = vx.reshape(y_shape)

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)

    operator = make_node("Flatten", ["x"], ["y"], **kwargs)
    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    assert tuple(vy.shape) == tuple(graph.outputs[0].shape), f"vy: {vy.shape}, graph.outputs[0]: {graph.outputs[0].shape}"
    generate_kernel_test_case(
        description=f"[ONNX] Flatten {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test_with_axis():
    template(x_shape=[2, 3, 4, 5], axis=2, kwargs={"axis": 2})


def test_without_axis():
    template(x_shape=[2, 3, 4, 5], axis=1, kwargs={})
