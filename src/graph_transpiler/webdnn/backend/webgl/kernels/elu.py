from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.elu import Elu

register_elementwise_kernel(Elu, "y = x0 < 0.0 ? (exp(x0) - 1.0) : x0;")
