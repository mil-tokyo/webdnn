import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, description: str = ""):
    vx = np.random.rand(*x_shape)
    vy = np.mean(vx, axis=tuple(range(2, vx.ndim)), keepdims=False)

    x = make_tensor_value_info("x", x_shape)
    y = make_tensor_value_info("y", vy.shape)
    operator = make_node("GlobalAveragePool", ["x"], ["y"])
    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] GlobalAveragePool {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 3, 4, 5])
