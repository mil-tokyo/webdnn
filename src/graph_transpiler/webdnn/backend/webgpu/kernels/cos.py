from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.cos import Cos

register_elementwise_kernel(Cos, "y = cos(x0);")
