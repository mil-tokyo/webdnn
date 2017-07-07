from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sigmoid import Sigmoid

register_elementwise_kernel(Sigmoid, "y = tanh(0.5f * x0) * 0.5f + 0.5f;")
