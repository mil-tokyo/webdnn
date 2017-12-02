from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.asinh import Asinh

register_elementwise_kernel(Asinh, "y = log(x0+sqrt(pow(x0, 2.0) + 1.0));")
