import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, blocksize, description: str = ""):
    N, C, H, W = x_shape
    vx = np.random.rand(*x_shape)

    vy = vx.reshape([N, C, H // blocksize, blocksize, W // blocksize, blocksize])
    vy = vy.transpose([0, 3, 5, 1, 2, 4])
    vy = vy.reshape([N, C * blocksize * blocksize, H // blocksize, W // blocksize])

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)
    operator = make_node("SpaceToDepth", ["x"], ["y"], blocksize=blocksize)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    assert list(vy.shape) == list(graph.outputs[0].shape)

    generate_kernel_test_case(
        description=f"[ONNX] SpaceToDepth {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 5, 10, 20], blocksize=2)
