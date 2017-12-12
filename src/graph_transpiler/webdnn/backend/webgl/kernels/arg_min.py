from webdnn.backend.webgl.kernels.reduce import register_reduction_kernel
from webdnn.graph.operators.arg_min import ArgMin

register_reduction_kernel(ArgMin,
                          pre_reduction_snippet="int min_i = 0; float min_x = +1.0e10;",
                          body_snippet="if (x < min_x) { min_x = x; min_i = i_x; }",
                          post_reduction_snippet="y = float(min_i);")
