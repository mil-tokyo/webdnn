from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.elementwise_add import ElementwiseAdd

register_elementwise_kernel(ElementwiseAdd, "y = x0 + x1;")
