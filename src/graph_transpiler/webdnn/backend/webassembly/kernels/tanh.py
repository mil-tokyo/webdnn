from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.tanh import Tanh

register_elementwise_kernel(Tanh, "y = tanh(x0);")
