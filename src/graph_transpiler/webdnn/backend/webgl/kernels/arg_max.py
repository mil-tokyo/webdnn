from webdnn.backend.webgl.kernels.reduce import register_reduction_kernel
from webdnn.graph.operators.arg_max import ArgMax

register_reduction_kernel(ArgMax,
                          pre_reduction_snippet="int max_i = 0; float max_x = -1.0e10;",
                          body_snippet="if (x > max_x) { max_x = x; max_i = i_x; }",
                          post_reduction_snippet="y = float(max_i);")
