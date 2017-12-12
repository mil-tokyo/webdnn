import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, split, axis, description: str = ""):
    vx = np.random.rand(*x_shape)
    sections = np.cumsum(split).tolist()[:-1]
    vys = np.split(vx, sections, axis=axis)

    x = make_tensor_value_info("x", vx.shape)
    ys = [make_tensor_value_info(f"y{i}", vy.shape) for i, vy in enumerate(vys)]
    operator = make_node("Split", ["x"], [y.name for y in ys], axis=axis, split=split)

    model = make_model([operator], [x], ys)

    graph = ONNXConverter().convert(model)

    for i, vy in enumerate(vys):
        assert tuple(vy.shape) == tuple(graph.outputs[i].shape), f"vys[{i}]: {vy.shape}, graph.outputs[{i}]: {graph.outputs[i].shape}"

    generate_kernel_test_case(
        description=f"[ONNX] Split {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[i]: vy for i, vy in enumerate(vys)},
    )


def test():
    template(x_shape=[2, 3, 20, 5], split=[4, 6, 3, 7], axis=2)
