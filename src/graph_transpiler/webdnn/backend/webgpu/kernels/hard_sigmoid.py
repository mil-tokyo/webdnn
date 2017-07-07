from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.hard_sigmoid import HardSigmoid

register_elementwise_kernel(HardSigmoid, """
y = x0 * 0.2f + 0.5f;
if (y < 0.0f) {
    y = 0.0f;
} else if (y > 1.0f) {
    y = 1.0f;
}
""")
