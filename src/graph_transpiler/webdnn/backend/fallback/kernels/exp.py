from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.exp import Exp

register_elementwise_kernel(Exp, "y = Math.exp(x0);")
