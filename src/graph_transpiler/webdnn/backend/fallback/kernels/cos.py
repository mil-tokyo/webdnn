from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.cos import Cos

register_elementwise_kernel(Cos, "y = Math.cos(x0);")
