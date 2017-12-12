import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(x_shape, pads, mode, value=None, description: str = ""):
    vx = np.random.rand(*x_shape)
    np_pads = [[b, e] for b, e in zip(pads[:vx.ndim], pads[vx.ndim:])]
    if mode == b"constant":
        vy = np.pad(vx, np_pads, mode="constant", constant_values=value)

    elif mode == b"reflect":
        vy = np.pad(vx, np_pads, mode="reflect")

    elif mode == b"edge":
        vy = np.pad(vx, np_pads, mode="symmetric")

    else:
        raise ValueError(mode)

    x = make_tensor_value_info("x", vx.shape)
    y = make_tensor_value_info("y", vy.shape)

    kwargs = {"pads": pads, "mode": mode}
    if value is not None:
        kwargs["value"] = value
    operator = make_node("Pad", ["x"], ["y"], **kwargs)

    model = make_model([operator], [x], [y])

    graph = ONNXConverter().convert(model)

    assert list(vy.shape) == list(graph.outputs[0].shape)

    generate_kernel_test_case(
        description=f"[ONNX] Pad {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test_constant():
    template(x_shape=[2, 3, 4, 5], pads=[1, 2, 3, 4, 5, 6, 7, 8], mode=b"constant", value=1.0)


def test_reflect():
    template(x_shape=[10, 11, 12, 13], pads=[1, 2, 3, 4, 5, 6, 7, 8], mode=b"reflect")


def test_edge():
    template(x_shape=[10, 11, 12, 13], pads=[1, 2, 3, 4, 5, 6, 7, 8], mode=b"edge")
