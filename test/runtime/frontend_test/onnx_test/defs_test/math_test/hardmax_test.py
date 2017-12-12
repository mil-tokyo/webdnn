import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter
from webdnn.util.misc import mul


@wrap_template
def template(x_shape, axis, description: str = ""):
    np_axis = 1 if axis is None else axis
    vx = np.random.rand(*x_shape)
    new_shape = [mul(vx.shape[:np_axis]), mul(vx.shape[np_axis:])]
    max_i = np.argmax(vx.reshape(new_shape), axis=1)
    vy = np.zeros(new_shape)
    vy[np.arange(vy.shape[0]), max_i] = 1

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)

    kwargs = {}
    if axis is not None:
        kwargs["axis"] = axis
    operator = make_node("Hardmax", ["x"], ["y"], **kwargs)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    assert tuple(vy.shape) == tuple(graph.outputs[0].shape), f"vy: {vy.shape}, graph.outputs[0]: {graph.outputs[0].shape}"
    generate_kernel_test_case(
        description=f"[ONNX] Hardmax {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 3, 4, 5], axis=1)


def test_no_axis():
    template(x_shape=[2, 3, 4, 5], axis=None)


def test_most_inner_axis():
    template(x_shape=[2, 3, 4, 5], axis=3)


def test_most_outer_axis():
    template(x_shape=[2, 3, 4, 5], axis=0)
