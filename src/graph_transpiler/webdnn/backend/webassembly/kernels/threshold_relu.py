from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.threshold_relu import ThresholdRelu

register_elementwise_kernel(ThresholdRelu,
                            "y = x0 > threshold ? x0 : 0;",
                            {"threshold": lambda op: op.parameters["threshold"]})
