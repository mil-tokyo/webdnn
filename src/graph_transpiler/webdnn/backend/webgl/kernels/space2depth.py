from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import get_output_position
from webdnn.backend.webgl.kernels.util import texel_fetch
from webdnn.graph.axis import Axis
from webdnn.graph.operators.space2depth import Space2Depth
from webdnn.graph.order import OrderNHWC


@WebGLDescriptorGenerator.register_handler(Space2Depth)
def space2depth(op: Space2Depth) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]
    r = op.parameters['r']
    C1 = x.shape_dict[Axis.C]

    assert x.order.check_same_axes(OrderNHWC)
    assert y.order.check_same_axes(OrderNHWC)
    assert ChannelMode.get(x) == ChannelModeEnum.R
    assert ChannelMode.get(y) == ChannelModeEnum.R

    code = KernelCode(["""
    void main() {
        ivec4 variable_position_y = """, get_output_position(y), f""";

        int n = variable_position_y[{y.order.axes_dict[Axis.N]}];
        int h2 = variable_position_y[{y.order.axes_dict[Axis.H]}];
        int w2 = variable_position_y[{y.order.axes_dict[Axis.W]}];
        int c2 = variable_position_y[{y.order.axes_dict[Axis.C]}];

        int c1 = mod(c2, {C1});
        int h1 = h2 * {r} + c2 / {C1} / {r};
        int w1 = w2 * {r} + mod(c2 / {C1}, {r});

        ivec4 variable_position_x;
        variable_position_x[{x.order.axes_dict[Axis.N]}] = n;
        variable_position_x[{x.order.axes_dict[Axis.H]}] = h1;
        variable_position_x[{x.order.axes_dict[Axis.W]}] = w1;
        variable_position_x[{x.order.axes_dict[Axis.C]}] = c1;

        gl_FragColor.r = """, texel_fetch(x, "variable_position_x"), """.r;
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
