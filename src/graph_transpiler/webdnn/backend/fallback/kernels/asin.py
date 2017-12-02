from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.asin import Asin

register_elementwise_kernel(Asin, "y = Math.asin(x0);")
