import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, perm=None, description: str = ""):
    vx = np.random.rand(*x_shape)
    vy = np.transpose(vx, perm)

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)

    if perm is None:
        operator = make_node("Transpose", ["x"], ["y"])
    else:
        operator = make_node("Transpose", ["x"], ["y"], perm=perm)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    assert list(vy.shape) == list(graph.outputs[0].shape)

    generate_kernel_test_case(
        description=f"[ONNX] Transpose {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 3, 4, 5], perm=[2, 0, 3, 1])


def test_omit_perm():
    template(x_shape=[2, 3, 4, 5], perm=None)
