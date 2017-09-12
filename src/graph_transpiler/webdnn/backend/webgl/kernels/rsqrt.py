from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.rsqrt import Rsqrt

register_elementwise_kernel(Rsqrt, "y = inversesqrt(x0);")
