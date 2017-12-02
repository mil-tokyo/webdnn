from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.acosh import Acosh

register_elementwise_kernel(Acosh, "y = Math.acosh(x0);")
