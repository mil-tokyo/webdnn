from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.atan import Atan

register_elementwise_kernel(Atan, "y = Math.atan(x0);")
