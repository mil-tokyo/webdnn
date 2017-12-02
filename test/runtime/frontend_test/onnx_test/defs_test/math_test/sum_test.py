import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, num_input=2, description: str = ""):
    vxs = [np.random.rand(*x_shape) for _ in range(num_input)]
    vy = np.zeros(x_shape)
    for vx in vxs:
        vy += vx

    xs = [make_tensor_value_info(f"x{i}", vxs[i].shape) for i in range(num_input)]
    y = make_tensor_value_info("y", vy.shape)

    operator = make_node("Sum", [x.name for x in xs], ["y"])

    model = make_model([operator], xs, [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] Sum {description}",
        graph=graph,
        inputs={v: x for v, x in zip(graph.inputs, vxs)},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 3, 4, 5], num_input=2)


def test_add_3_tensors():
    template(x_shape=[2, 3, 4, 5], num_input=3)
