from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.scalar_pow import ScalarPow

register_elementwise_kernel(ScalarPow, "y = pow(x0, float(value));", {
    "value": lambda op: op.parameters["value"]
})
