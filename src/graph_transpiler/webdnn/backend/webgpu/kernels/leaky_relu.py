from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.leaky_relu import LeakyRelu

register_elementwise_kernel(LeakyRelu,
                            "y = x0 > 0 ? x0 : (x0 * slope);",
                            {"slope": lambda op: op.parameters["slope"]})
