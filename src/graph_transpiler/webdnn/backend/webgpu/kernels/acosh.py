from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.acosh import Acosh
from webdnn.graph.operators.atan import Atan

register_elementwise_kernel(Acosh, "y = acosh(x0);")
