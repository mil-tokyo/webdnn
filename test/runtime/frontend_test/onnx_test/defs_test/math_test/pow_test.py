import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x0_shape, x1_shape, description: str = ""):
    vx0 = np.random.rand(*x0_shape)
    vx1 = np.random.rand(*x1_shape)
    vy = vx0 ** vx1

    x0 = make_tensor_value_info("x0", vx0.shape)
    x1 = make_tensor_value_info("x1", vx1.shape)
    y = make_tensor_value_info("y", vy.shape)

    operator = make_node("Pow", ["x0", "x1"], ["y"])

    model = make_model([operator], [x0, x1], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] Pow {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: vx0,
            graph.inputs[1]: vx1
        },
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x0_shape=[2, 3, 4, 5], x1_shape=[2, 3, 4, 5])


def test_implicit_broadcast():
    template(x0_shape=[2, 3, 4, 5], x1_shape=[2, 1, 4, 1])
