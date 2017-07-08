from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.elementwise_pow import ElementwisePow

register_elementwise_kernel(ElementwisePow, "y = pow(x0, x1);")
