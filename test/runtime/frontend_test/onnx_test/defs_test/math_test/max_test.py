import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(n_x, x_shape, description: str = ""):
    vxs = [np.random.rand(*x_shape) for _ in range(n_x)]

    vys = list(vxs)
    while len(vys) > 1:
        vx1, vx2 = vys.pop(0), vys.pop(0)
        vy = np.maximum(vx1, vx2)
        vys.append(vy)
    vy = vys[0]

    xs = [make_tensor_value_info(f"x{i}", vx.shape) for i, vx in enumerate(vxs)]
    y = make_tensor_value_info("y", vy.shape)

    operator = make_node("Max", [x.name for x in xs], ["y"])

    model = make_model([operator], xs, [y])

    graph = ONNXConverter().convert(model)

    assert tuple(vy.shape) == tuple(graph.outputs[0].shape), f"vy: {vy.shape}, graph.outputs[0]: {graph.outputs[0].shape}"
    generate_kernel_test_case(
        description=f"[ONNX] Max {description}",
        graph=graph,
        inputs={graph.inputs[i]: vx for i, vx in enumerate(vxs)},
        expected={graph.outputs[0]: vy},
    )


def test_2():
    template(n_x=2, x_shape=[2, 3, 4, 5])


def test_3():
    template(n_x=3, x_shape=[2, 3, 4, 5])


def test_4():
    template(n_x=4, x_shape=[2, 3, 4, 5])
