from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.atanh import Atanh

register_elementwise_kernel(Atanh, "y = 0.5 * log((1.0 + x0)/(1.0 - x0));")
