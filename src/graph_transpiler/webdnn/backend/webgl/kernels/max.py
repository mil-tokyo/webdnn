from webdnn.backend.webgl.kernels.reduce import register_reduction_kernel
from webdnn.graph.operators.max import Max

register_reduction_kernel(Max,
                          pre_reduction_snippet="y = -1.0e10;",  # set very small value
                          body_snippet="y = x > y ? x : y;")
