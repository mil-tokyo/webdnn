from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.abs import Abs

register_elementwise_kernel(Abs, "y = abs(x0);")
