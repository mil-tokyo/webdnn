from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sqrt import Sqrt

register_elementwise_kernel(Sqrt, "y = sqrt(x0);")
