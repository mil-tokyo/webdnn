from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.greater import Greater

register_elementwise_kernel(Greater, "y = x0 > x1 ? 1.0 : 0.0;")
