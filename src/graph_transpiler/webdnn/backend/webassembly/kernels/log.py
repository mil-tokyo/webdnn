from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.log import Log

register_elementwise_kernel(Log, "y = log(x0);")
