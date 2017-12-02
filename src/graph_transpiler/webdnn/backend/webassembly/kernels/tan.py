from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.tan import Tan

register_elementwise_kernel(Tan, "y = tan(x0);")
