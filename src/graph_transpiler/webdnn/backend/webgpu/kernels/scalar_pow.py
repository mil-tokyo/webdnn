from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.scalar_pow import ScalarPow

register_elementwise_kernel(ScalarPow,
                            "y = pow(x0, value);",
                            {"value": lambda op: op.parameters["value"]})
