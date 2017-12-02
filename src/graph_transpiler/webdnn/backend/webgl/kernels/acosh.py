from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.acosh import Acosh

register_elementwise_kernel(Acosh, "y = log(x0+sqrt(pow(x0, 2.0) - 1.0));")
