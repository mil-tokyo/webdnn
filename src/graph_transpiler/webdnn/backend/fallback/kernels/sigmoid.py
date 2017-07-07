from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sigmoid import Sigmoid

register_elementwise_kernel(Sigmoid, "y = 1.0 / (1.0 + Math.exp(-x0));")
