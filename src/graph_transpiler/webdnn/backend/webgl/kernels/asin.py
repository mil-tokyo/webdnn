from webdnn.backend.webgl.kernels.elementwise import register_elementwise_kernel
from webdnn.graph.operators.acosh import Acosh
from webdnn.graph.operators.asin import Asin
from webdnn.graph.operators.asinh import Asinh

register_elementwise_kernel(Asin, "y = asin(x0);")
