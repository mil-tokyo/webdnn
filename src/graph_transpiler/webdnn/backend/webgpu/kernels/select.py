from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.select import Select

register_elementwise_kernel(Select, "y = (x0 == 1.0f ? x1 : x2);")
