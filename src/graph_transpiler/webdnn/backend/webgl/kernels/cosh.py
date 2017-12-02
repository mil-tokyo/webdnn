from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.cosh import Cosh

register_elementwise_kernel(Cosh, "y = (exp(x0) + exp(-x0))/2.0;")
