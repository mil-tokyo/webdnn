from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.clipped_relu import ClippedRelu

register_elementwise_kernel(ClippedRelu,
                            "y = x0 < 0 ? 0 : x0 > cap ? cap : x0;",
                            {"cap": lambda op: op.parameters["cap"]})
