from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sqrt import Sqrt

register_elementwise_kernel(Sqrt, "y = Math.sqrt(x0);")
