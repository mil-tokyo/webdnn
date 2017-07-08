from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.elementwise_pow import ElementwisePow

register_elementwise_kernel(ElementwisePow, "y = Math.pow(x0, x1);")
