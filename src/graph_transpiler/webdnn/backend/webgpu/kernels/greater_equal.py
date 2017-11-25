from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.greater_equal import GreaterEqual

register_elementwise_kernel(GreaterEqual, "y = x0 >= x1 ? 1.0 : 0.0;")
