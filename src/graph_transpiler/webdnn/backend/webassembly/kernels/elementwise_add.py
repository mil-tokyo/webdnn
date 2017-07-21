from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.elementwise_add import ElementwiseAdd

register_elementwise_kernel(ElementwiseAdd, "y = x0 + x1;")
register_elementwise_kernel(AxiswiseBias, "y = x0 + x1;")
