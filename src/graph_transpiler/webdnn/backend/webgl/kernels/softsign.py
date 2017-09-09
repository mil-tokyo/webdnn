from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.softsign import Softsign

register_elementwise_kernel(Softsign, "y = x0 / (abs(x0) + 1.0);")
