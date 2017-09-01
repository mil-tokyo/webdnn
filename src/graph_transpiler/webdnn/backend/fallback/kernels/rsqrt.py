from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.rsqrt import Rsqrt

register_elementwise_kernel(Rsqrt, "y = 1.0 / Math.sqrt(x0);")
