from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.elementwise_div import ElementwiseDiv

register_elementwise_kernel(ElementwiseDiv, "y = x0 / x1;")
