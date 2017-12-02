from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.tan import Tan

register_elementwise_kernel(Tan, "y = Math.tan(x0);")
