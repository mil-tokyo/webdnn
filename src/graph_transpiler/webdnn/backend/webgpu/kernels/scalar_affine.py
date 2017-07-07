from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.scalar_affine import ScalarAffine

register_elementwise_kernel(ScalarAffine,
                            "y = x0 * scale + bias;",
                            {"scale": lambda op: op.parameters["scale"],
                             "bias": lambda op: op.parameters["bias"], })
