from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.leaky_relu import LeakyRelu

register_elementwise_kernel(LeakyRelu, "y = ((1.0 + slope) * x0 + (1.0 - slope) * abs(x0)) * 0.5;", {
    "slope": lambda op: op.parameters["slope"]
})
