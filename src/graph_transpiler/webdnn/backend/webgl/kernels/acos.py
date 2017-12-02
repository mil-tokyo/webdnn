from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.acos import Acos

register_elementwise_kernel(Acos, "y = acos(x0);")
