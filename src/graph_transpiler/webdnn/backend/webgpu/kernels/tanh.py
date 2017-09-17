from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.tanh import Tanh

# In fast math mode, tanh(x) is implemented as
# (t – 1.0)/(t + 1.0) where t = exp(2.0 * x)
# (from Metal Shading Language Specification)
# and it easily overflow and produces NaN when x is large (negative large x is ok).
# When abs(x) >= 10.0, tanh will saturate in float precision,
# so output the constant value.
register_elementwise_kernel(Tanh, "y = (x0 >= 10.0 ? 1.0 : tanh(x0));")
