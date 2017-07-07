from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.softplus import Softplus

register_elementwise_kernel(Softplus,
                            "y = Math.log(1 + Math.exp(beta * x0)) / beta;",
                            {"beta": lambda op: op.parameters["beta"]})
