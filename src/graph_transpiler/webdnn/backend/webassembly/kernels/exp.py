from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.exp import Exp

register_elementwise_kernel(Exp, "y = exp(x0);")
