from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.asinh import Asinh

register_elementwise_kernel(Asinh, "y = asinh(x0);")
