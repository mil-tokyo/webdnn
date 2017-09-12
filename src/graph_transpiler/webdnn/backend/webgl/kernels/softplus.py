from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.softplus import Softplus

register_elementwise_kernel(Softplus, "y = log(1.0 + exp(beta * x0)) / beta;", {
    "beta": lambda op: op.parameters["beta"]
})
