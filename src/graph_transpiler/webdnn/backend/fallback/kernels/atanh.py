from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.atanh import Atanh

register_elementwise_kernel(Atanh, "y = Math.atanh(x0);")
