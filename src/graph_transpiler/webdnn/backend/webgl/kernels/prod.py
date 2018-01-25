from webdnn.backend.webgl.kernels.reduce import register_reduction_kernel
from webdnn.graph.operators.prod import Prod

register_reduction_kernel(Prod,
                          pre_reduction_snippet="y = 1.0;",
                          body_snippet="y *= x;")
