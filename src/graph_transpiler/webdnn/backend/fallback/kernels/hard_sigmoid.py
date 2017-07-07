from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.hard_sigmoid import HardSigmoid

register_elementwise_kernel(HardSigmoid, """
y = x0 * 0.2 + 0.5;
if (y < 0.0) {
    y = 0.0;
} else if (y > 1.0) {
    y = 1.0;
}
""")
