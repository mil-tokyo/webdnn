from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.tanh import Tanh

register_elementwise_kernel(Tanh, "y = (exp(x0) - exp(-x0)) / (exp(x0) + exp(-x0));")
