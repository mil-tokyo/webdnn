from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.acosh import Acosh

register_elementwise_kernel(Acosh, "y = acosh(x0);")
