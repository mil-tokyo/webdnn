from webdnn.backend.webgl.kernels.reduce import register_reduction_kernel
from webdnn.graph.operators.sum import Sum

register_reduction_kernel(Sum,
                          pre_reduction_snippet="y = 0.0;",
                          body_snippet="y += x;")
