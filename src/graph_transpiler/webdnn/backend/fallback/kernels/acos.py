from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.acos import Acos

register_elementwise_kernel(Acos, "y = Math.acos(x0);")
