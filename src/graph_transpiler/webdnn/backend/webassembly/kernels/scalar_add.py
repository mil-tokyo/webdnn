from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.scalar_add import ScalarAdd

register_elementwise_kernel(ScalarAdd,
                            "y = x0 + value;",
                            {"value": lambda op: op.parameters["value"]})
