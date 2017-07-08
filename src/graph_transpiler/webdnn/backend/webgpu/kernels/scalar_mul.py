from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.scalar_mul import ScalarMul

register_elementwise_kernel(ScalarMul,
                            "y = x0 * value;",
                            {"value": lambda op: op.parameters["value"]})
