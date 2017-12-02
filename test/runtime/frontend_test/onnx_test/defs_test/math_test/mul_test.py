import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x0_shape, x1_shape, broadcast=0, axis=None, description: str = ""):
    vx0 = np.random.rand(*x0_shape)
    vx1 = np.random.rand(*x1_shape)
    if axis is not None:
        # onnx-style broadcast
        vx1 = vx1[(None,) * axis + (...,) + (None,) * (vx0.ndim - vx1.ndim - axis)]

    vy = vx0 * vx1

    x0 = make_tensor_value_info("x0", x0_shape)
    x1 = make_tensor_value_info("x1", x1_shape)
    y = make_tensor_value_info("y", vy.shape)

    kwargs = {"broadcast": broadcast}
    if axis is not None:
        kwargs["axis"] = axis
    operator = make_node("Mul", ["x0", "x1"], ["y"], **kwargs)

    model = make_model([operator], [x0, x1], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] Mul {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: vx0,
            graph.inputs[1]: vx1
        },
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x0_shape=[2, 3, 4, 5], x1_shape=[2, 3, 4, 5])


def test_broadcast1():
    template(x0_shape=[2, 3, 4, 5], x1_shape=[1], broadcast=1)


def test_broadcast2():
    template(x0_shape=[2, 3, 4, 5], x1_shape=[5], broadcast=1)


def test_broadcast3():
    template(x0_shape=[2, 3, 4, 5], x1_shape=[4, 5], broadcast=1)


def test_broadcast4():
    template(x0_shape=[2, 3, 4, 5], x1_shape=[3, 4], broadcast=1, axis=1)


def test_broadcast5():
    template(x0_shape=[2, 3, 4, 5], x1_shape=[2], broadcast=1, axis=0)
