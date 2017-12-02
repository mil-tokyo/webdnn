import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, alpha=1.0, description: str = ""):
    vx = np.random.rand(*x_shape) - 0.5
    vy = vx.copy()
    vy[vx < 0] = np.exp(vy[vx < 0]) - 1

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)
    operator = make_node("Elu", ["x"], ["y"], alpha=alpha)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] Elu {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 3, 4, 5])

# TODO: Not supported yet
# def test_alpha():
#     template(x0_shape=[2, 3, 4, 5], alpha=0.3)
