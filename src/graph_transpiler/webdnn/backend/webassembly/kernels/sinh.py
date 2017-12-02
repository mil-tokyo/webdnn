from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sinh import Sinh

register_elementwise_kernel(Sinh, "y = sinh(x0);")
