from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.transpose import Transpose

register_elementwise_kernel(Transpose, "y = x0;")
