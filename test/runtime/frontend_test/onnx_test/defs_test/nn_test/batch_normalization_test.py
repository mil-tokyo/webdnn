import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(N=2, H=5, W=5, C=7, epsilon: float = 1e-5, description: str = ""):
    # spatial = 0 is not supported
    x_shape = [N, C, H, W]

    def expand(v):
        return v[np.newaxis, :, np.newaxis, np.newaxis]

    # computing test case with float64 makes difference
    def randfloat(*shape):
        return np.random.rand(*shape).astype(np.float32)

    vx = randfloat(*x_shape)
    vscale = randfloat(C)
    vB = randfloat(C)
    vmean = randfloat(C)
    vvar = randfloat(C)
    vy = (vx - expand(vmean)) / np.sqrt(expand(vvar) + epsilon) * expand(vscale) + expand(vB)

    x = make_tensor_value_info("x", x_shape)
    scale = make_tensor_value_info("scale", [C])
    B = make_tensor_value_info("B", [C])
    mean = make_tensor_value_info("mean", [C])
    var = make_tensor_value_info("var", [C])
    y = make_tensor_value_info("y", vy.shape)

    kwargs = {
        "epsilon": epsilon
    }
    operator = make_node("BatchNormalization", ["x", "scale", "B", "mean", "var"], ["y"], **kwargs)
    model = make_model([operator], [x, scale, B, mean, var], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] BatchNormalization {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx,
                graph.inputs[1]: vscale,
                graph.inputs[2]: vB,
                graph.inputs[3]: vmean,
                graph.inputs[4]: vvar},
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_epsilon():
    template(epsilon=1e-1)
