from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.elementwise_add_relu import ElementwiseAddRelu

register_elementwise_kernel(ElementwiseAddRelu, "y = ((x0 + x1) > 0) ? (x0 + x1) : 0;")
