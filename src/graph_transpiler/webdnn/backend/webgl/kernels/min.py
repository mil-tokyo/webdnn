from webdnn.backend.webgl.kernels.reduce import register_reduction_kernel
from webdnn.graph.operators.min import Min

register_reduction_kernel(Min,
                          pre_reduction_snippet="y = +1.0e10;",  # set very large value
                          body_snippet="y = x < y ? x : y;")
