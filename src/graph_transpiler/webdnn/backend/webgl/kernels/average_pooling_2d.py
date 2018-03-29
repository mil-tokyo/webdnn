from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import texel_fetch, get_output_position, \
    change_order
from webdnn.graph.axis import Axis
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.order import OrderNHWC


@WebGLDescriptorGenerator.register_handler(AveragePooling2D)
def average_pooling_2d(op: AveragePooling2D) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert x.order.check_same_axes(OrderNHWC)
    assert y.order.check_same_axes(OrderNHWC)
    assert ChannelMode.get(x) == ChannelModeEnum.R
    assert ChannelMode.get(y) == ChannelModeEnum.R

    if op.parameters["divide_without_padding"]:
        divider_init = "float divider = 1e-8;"
        divider_add = "divider += 1.0;"
        divider_get = "divider"
    else:
        divider_init = ""
        divider_add = ""
        divider_get = str(float(op.ksize[0] * op.ksize[1]))

    code = KernelCode(["""
void main() {
    ivec4 variable_position_y = """, change_order(get_output_position(y), y.order, OrderNHWC), f""";
    int n = variable_position_y.x;
    int h2 = variable_position_y.y;
    int w2 = variable_position_y.z;
    int c = variable_position_y.w;

    float sum = 0.0;
    {divider_init}

    for (int kh = 0; kh < {op.KH}; kh++) {{
        int h1 = h2 * {op.SH} - {op.PH} + kh;
        if (h1 < 0 || h1 >= {x.shape_dict[Axis.H]}) continue;

        for (int kw = 0; kw < {op.KW}; kw++) {{
            int w1 = w2 * {op.SW} - {op.PW} + kw;
            if (w1 < 0 || w1 >= {x.shape_dict[Axis.W]}) continue;

            sum += """, texel_fetch(x, change_order("vec4(n, h1, w1, c)", OrderNHWC, x.order)), f""".r;
            {divider_add}
        }}
    }}

    gl_FragColor.r = sum / {divider_get};
}}
"""], name=op.__class__.__name__)
    source = code.generate()

    return [Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        y
    )]
