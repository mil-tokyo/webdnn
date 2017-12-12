from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import texel_fetch, get_output_position, change_order
from webdnn.graph.axis import Axis
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.order import OrderNHWC


@WebGLDescriptorGenerator.register_handler(Depth2Space)
def depth2space(op: Depth2Space) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]
    r = op.parameters['r']
    C2 = y.shape_dict[Axis.C]

    assert x.order.check_same_axes(OrderNHWC)
    assert y.order.check_same_axes(OrderNHWC)
    assert ChannelMode.get(x) == ChannelModeEnum.R
    assert ChannelMode.get(y) == ChannelModeEnum.R

    code = KernelCode(["""
void main() {
    ivec4 variable_position_y = """, change_order(get_output_position(y), y.order, OrderNHWC), f""";

    int n = variable_position_y.x;
    int h2 = variable_position_y.y;
    int w2 = variable_position_y.z;
    int c2 = variable_position_y.w;

    int h1 = h2 / {r};
    int w1 = w2 / {r};
    int c1 = c2 + (w2-w1*{r})*{C2} + (h2-h1*{r})*{C2}*{r};

    gl_FragColor.r = """, texel_fetch(x, change_order("vec4(n, h1, w1, c1)", OrderNHWC, x.order)), """.r;
}
"""], name=op.__class__.__name__)
    source = code.generate()
    return [Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        y
    )]
