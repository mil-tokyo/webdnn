from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.cosh import Cosh

register_elementwise_kernel(Cosh, "y = cosh(x0);")
