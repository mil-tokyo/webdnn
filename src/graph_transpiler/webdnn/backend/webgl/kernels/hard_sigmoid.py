from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.hard_sigmoid import HardSigmoid

register_elementwise_kernel(HardSigmoid, """
    y = x0 * 0.2 + 0.5;
    y = (y < 0.0) ? 0.0 : (y > 1.0) ? 1.0 : y;
""")
