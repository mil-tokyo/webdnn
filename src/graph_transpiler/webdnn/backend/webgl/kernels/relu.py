from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.relu import Relu

register_elementwise_kernel(Relu, "y = x0 < 0.0 ? 0.0 : x0;")
