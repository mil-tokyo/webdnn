from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sin import Sin

register_elementwise_kernel(Sin, "y = sin(x0);")
