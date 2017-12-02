from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.asin import Asin

register_elementwise_kernel(Asin, "y = asin(x0);")
