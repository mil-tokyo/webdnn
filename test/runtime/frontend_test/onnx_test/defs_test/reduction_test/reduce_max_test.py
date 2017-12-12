import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, axes, keepdims=None, description: str = ""):
    vx = np.random.rand(*x_shape)
    vy = np.max(vx, axis=tuple(axes), keepdims=True if keepdims is None else keepdims)

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)

    kwargs = {"axes": axes}
    if keepdims is not None:
        kwargs["keepdims"] = keepdims
    operator = make_node("ReduceMax", ["x"], ["y"], **kwargs)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    assert tuple(vy.shape) == tuple(graph.outputs[0].shape), f"vy: {vy.shape}, graph.outputs[0]: {graph.outputs[0].shape}"
    generate_kernel_test_case(
        description=f"[ONNX] ReduceMax {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[1, 3, 4, 5], axes=[2])


def test_keepdim():
    template(x_shape=[1, 3, 4, 5], axes=[2], keepdims=True)


def test_not_keepdim():
    template(x_shape=[1, 3, 4, 5], axes=[2], keepdims=False)


def test_multi_axes():
    template(x_shape=[1, 3, 4, 5], axes=[2, 3])


def test_all_axes():
    template(x_shape=[1, 3, 4, 5], axes=[0, 1, 2, 3])
