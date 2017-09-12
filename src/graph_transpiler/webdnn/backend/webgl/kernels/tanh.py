from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.tanh import Tanh

register_elementwise_kernel(Tanh, """
float v = exp(-2.0*abs(x0));
y = (1.0 - v) / (1.0 + v) * sign(x0);
""")
