from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sinh import Sinh

register_elementwise_kernel(Sinh, "y = Math.sinh(x0);")
