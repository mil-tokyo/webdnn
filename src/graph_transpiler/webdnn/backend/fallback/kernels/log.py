from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.log import Log

register_elementwise_kernel(Log, "y = Math.log(x0);")
