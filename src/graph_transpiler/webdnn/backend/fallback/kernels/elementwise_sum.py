from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.elementwise_sum import ElementwiseSum

register_elementwise_kernel(ElementwiseSum, "y = x0 + x1;")
