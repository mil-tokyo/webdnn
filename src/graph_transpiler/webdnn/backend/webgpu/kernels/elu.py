from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.elu import Elu

register_elementwise_kernel(Elu, "y = x0 < 0.0 ? (exp(x0)-1) : x0;")
