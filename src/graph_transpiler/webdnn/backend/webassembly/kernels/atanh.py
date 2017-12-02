from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.atanh import Atanh

register_elementwise_kernel(Atanh, "y = atanh(x0);")
