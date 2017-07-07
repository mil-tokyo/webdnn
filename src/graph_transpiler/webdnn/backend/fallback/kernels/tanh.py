from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.tanh import Tanh

register_elementwise_kernel(Tanh, "y = Math.tanh(x0);")
