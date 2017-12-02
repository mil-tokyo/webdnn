import numpy as np

from test.runtime.frontend_test.onnx_test.util import make_node, make_tensor_value_info, make_model, make_tensor
from test.util import wrap_template, generate_kernel_test_case
from webdnn.frontend.onnx import ONNXConverter


@wrap_template
def template(value, description: str = ""):
    y = make_tensor_value_info("y", value.shape)
    operator = make_node("Constant", [""], ["y"], value=make_tensor("y_value", value))

    model = make_model([operator], [], [y])

    graph = ONNXConverter().convert(model)

    generate_kernel_test_case(
        description=f"[ONNX] Constant {description}",
        graph=graph,
        inputs={},
        expected={graph.outputs[0]: value},
    )


def test():
    template(value=np.random.rand(2, 3, 4, 5), description="")
