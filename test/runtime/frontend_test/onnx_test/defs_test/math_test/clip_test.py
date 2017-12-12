import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, min_x, max_x, description: str = ""):
    vx = np.random.rand(*x_shape)
    vy = np.clip(vx, min_x, max_x)

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)
    operator = make_node("Clip", ["x"], ["y"], min=min_x, max=max_x)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] Clip {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy}
    )


def test():
    template(x_shape=[2, 3, 4, 5], min_x=0.2, max_x=0.8)


def test_same():
    template(x_shape=[2, 3, 4, 5], min_x=0.5, max_x=0.5)
