from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.sigmoid import Sigmoid

register_elementwise_kernel(Sigmoid, "y = (x0 >= 20.0f ? 1.0f : tanh(0.5f * x0) * 0.5f + 0.5f);")
