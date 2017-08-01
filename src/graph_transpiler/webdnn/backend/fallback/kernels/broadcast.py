from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.broadcast import Broadcast

register_elementwise_kernel(Broadcast, "y = x0;")
