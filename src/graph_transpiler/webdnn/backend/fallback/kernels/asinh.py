from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.asinh import Asinh

register_elementwise_kernel(Asinh, "y = Math.asinh(x0);")
