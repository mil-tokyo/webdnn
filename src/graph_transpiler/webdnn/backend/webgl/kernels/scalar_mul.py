from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.scalar_mul import ScalarMul

register_elementwise_kernel(ScalarMul, "y = x0 * float(value);", {
    "value": lambda op: op.parameters["value"]
})
