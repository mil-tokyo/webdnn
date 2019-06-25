from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sqrt import Sqrt

register_elementwise_kernel(Sqrt, "y = sqrt(x0);")
