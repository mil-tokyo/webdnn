from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.select import Select

register_elementwise_kernel(Select, "y = (x0 == 1.0 ? x1 : x2);")
