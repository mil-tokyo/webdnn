from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sinh import Sinh

register_elementwise_kernel(Sinh, "y = (exp(x0) - exp(-x0))/2.0;")
