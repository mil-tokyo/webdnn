import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(xs_shape, axis, description: str = ""):
    vxs = [np.random.rand(*x_shape) for x_shape in xs_shape]
    vy = np.concatenate(vxs, axis)

    xs = [make_tensor_value_info(f"x{i}", vx.shape) for i, vx in enumerate(vxs)]
    y = make_tensor_value_info("y", vy.shape)
    operator = make_node("Concat", [x.name for x in xs], ["y"], axis=axis)

    model = make_model([operator], xs, [y])

    graph = ONNXConverter().convert(model)

    assert tuple(vy.shape) == tuple(graph.outputs[0].shape), f"vy: {vy.shape}, graph.outputs[0]: {graph.outputs[0].shape}"
    generate_kernel_test_case(
        description=f"[ONNX] Concat {description}",
        graph=graph,
        inputs={graph.inputs[i]: vx for i, vx in enumerate(vxs)},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(xs_shape=[[2, 3, 4, 5], [2, 1, 4, 5]], axis=1)
