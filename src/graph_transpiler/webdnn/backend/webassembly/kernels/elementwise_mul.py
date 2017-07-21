from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.elementwise_mul import ElementwiseMul

register_elementwise_kernel(ElementwiseMul, "y = x0 * x1;")
register_elementwise_kernel(AxiswiseScale, "y = x0 * x1;")
